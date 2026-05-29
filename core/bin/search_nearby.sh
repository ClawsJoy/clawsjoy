#!/bin/bash
# search_nearby.sh - 搜索附近咖啡店
KEYWORD=${1:-咖啡店}
echo "{\"status\":\"success\",\"stores\":[
    {\"name\":\"星巴克\",\"distance\":\"200m\",\"inventory\":{\"拿铁\":true,\"美式\":true,\"卡布奇诺\":true}},
    {\"name\":\"瑞幸\",\"distance\":\"350m\",\"inventory\":{\"拿铁\":true,\"美式\":true,\"卡布奇诺\":false}},
    {\"name\":\"Costa\",\"distance\":\"500m\",\"inventory\":{\"拿铁\":false,\"美式\":true,\"卡布奇诺\":true}}
]}"
