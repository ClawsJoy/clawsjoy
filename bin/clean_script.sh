#!/bin/bash
# 清理脚本中的乱码
sed -i 's/\*\*\*//g' /tmp/script.txt
sed -i 's/###//g' /tmp/script.txt
sed -i 's/\[K\]//g' /tmp/script.txt
sed -i 's/AA//g' /tmp/script.txt
