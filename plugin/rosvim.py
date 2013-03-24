#!/usr/bin/env python
# encoding: utf-8

import vim
import vimp
import rosp
import rospkg
import subprocess


packages = dict()


def package():
    return packages[vimp.var['b:ros_package_name']]


def buf_enter():
    p = vimp.var['b:ros_package_name']
    if not p in packages:
        packages[p] = rosp.Package(p)
    if vimp.var['g:ros_make'] == 'all':
        cmd = 'set makeprg=rosmake\ ' + '\ '.join(packages.keys())
    else:
        cmd = 'set makeprg=rosmake\ ' + p
    vim.command(cmd)


def alternate():
    mapping = {'.h': '.cpp', '.cpp': '.h'}
    if vimp.buf.extension in mapping:
        altfile = vimp.buf.stem + mapping[vimp.buf.extension]
        for f in package().locate_files(altfile):
            vimp.edit(f)
            return
        print 'Nothing found!'
    else:
        print 'No alternate for this extension'


@vimp.function
def roscd(package_name):
    try:
        pkg = rosp.Package(package_name)
    except rospkg.ResourceNotFound:
        print 'Package {0} not found'.format(package_name)
        return
    vimp.lcd(pkg.path)


@vimp.function
def roscd_complete(arg_lead, cmd_line, cursor_pos):
    """
    Returns a list of complete suggestions for :Roscd command.

    Arguments
    ---------
    arg_lead:
        The leading portion of the argument currently being completed on.
    cmd_line:
        The entire command line.
    cursor_pos:
        The cursor position in the line (byte index).
    """
    return '\n'.join(rosp.Package.list())


@vimp.function
def rosed(package_name, *file_names):
    try:
        pkg = rosp.Package(package_name)
    except rospkg.ResourceNotFound:
        print 'Package {0} not found'.format(package_name)
        return
    for fn in file_names:
        for f in pkg.locate_files(fn):
            vimp.edit(f)


@vimp.function
def rosed_complete(arg_lead, cmd_line, cursor_pos):
    """
    Returns a list of complete suggestions for :Rosed command.

    Arguments
    ---------
    arg_lead:
        The leading portion of the argument currently being completed on.
    cmd_line:
        The entire command line.
    cursor_pos:
        The cursor position in the line (byte index).
    """
    args = cmd_line[0:int(cursor_pos)].split(' ')
    if len(args) == 2:
        # still entering package name
        return '\n'.join(rosp.Package.list())
    elif len(args) >= 3:
        # package name already entered
        try:
            pkg = rosp.Package(args[1])
        except rospkg.ResourceNotFound:
            return ''
        pattern = arg_lead + '*'
        return '\n'.join(list(pkg.locate_files(pattern, mode='filename')))


@vimp.function
def msg_complete(findstart, base):
    if findstart == '1':
        return 0
    else:
        msgs = subprocess.check_output(['rosmsg', 'list']).strip().split('\n')
        builtin = ['bool', 'int8', 'uint8', 'int16', 'uint16', 'int32',
                   'uint32', 'int64', 'uint64', 'float32', 'float64', 'string',
                   'time', 'duration', 'Header']
        return [m for m in builtin + msgs if m.startswith(base)]


@vimp.function
def launch_complete(findstart, base):
    def find_start():
        line = vim.current.line
        col = vim.current.window.cursor[1]
        while col > 0 and line[col - 1] != '"':
            col -= 1
        start = col
        while col > 0 and line[col - 1] != ' ':
            col -= 1
        field = line[col:start - 2]
        return (start, field)
    if findstart == '1':
        return find_start()[0]
    else:
        field = find_start()[1]
        if field == 'pkg':
            packages = sorted(rosp.Package.list())
            return [p for p in packages if p.startswith(base)]
        elif field == 'type':
            executables = ['not implemented']
            return executables
        else:
            return []
