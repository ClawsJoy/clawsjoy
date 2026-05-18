#!/bin/bash
case $1 in
    list)
        echo "可用的 TTS Skills:"
        ls -1 /home/flybo/clawsjoy/skills/ | grep tts-
        ;;
    use)
        [ -z "$2" ] && echo "请指定 skill 名称" && exit 1
        echo "export CLAWSJOY_TTS_SKILL=$2" >> ~/.bashrc
        echo "已设置 TTS Skill 为: $2"
        echo "请执行: source ~/.bashrc && pm2 restart clawsjoy-task"
        ;;
    install)
        if [ "$2" == "piper" ]; then
            echo "请运行: /home/flybo/clawsjoy/installers/install_piper_tts.sh"
        elif [ "$2" == "edge" ]; then
            echo "请运行: /home/flybo/clawsjoy/installers/install_edge_tts.sh"
        else
            echo "用法: tts_skill.sh install piper|edge"
        fi
        ;;
    *)
        echo "用法: tts_skill.sh {list|use <name>|install piper|edge}"
        ;;
esac
