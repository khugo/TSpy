cd server
export LD_LIBRARY_PATH=".:$LD_LIBRARY_PATH"
gdb ts3server_linux_x86 -x ../gdbcfg.txt -nw
