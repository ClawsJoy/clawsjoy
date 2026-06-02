# ClawsJoy v6.0 原子引擎检测报告

## 1. 软连接状态
./intelligence
./config/version/current
./bin
./templates/web
./models/models
./web/web
./lib
./piper/libespeak-ng.so
./piper/libonnxruntime.so
./piper/libespeak-ng.so.1
./core/config
./core/bin/convert_format
./core/bin/video_compress
./core/bin/video_trim
./core/bin/extract_audio
./core/bin/get_video_info
./core/bin/video_concat
./core/bin/video_download
./core/bin/write_design
./core/bin/concat_video

## 2. 引擎函数完整性

| 引擎 | get_stats | process | reload | execute |
|------|-----------|---------|--------|---------|
| active | 0
0 | 0
0 | 0
0 | 0
0 |
| audit | 1 | 0
0 | 0
0 | 0
0 |
| document | 1 | 0
0 | 0
0 | 0
0 |
| event | 1 | 0
0 | 0
0 | 0
0 |
| hook | 1 | 0
0 | 0
0 | 1 |
| knowledge | 1 | 0
0 | 0
0 | 0
0 |
| memory | 0
0 | 0
0 | 0
0 | 0
0 |
| monitor | 1 | 0
0 | 0
0 | 0
0 |
| planning | 1 | 0
0 | 0
0 | 0
0 |
| profile | 0
0 | 0
0 | 0
0 | 0
0 |
| ratelimit | 1 | 0
0 | 0
0 | 0
0 |
| reasoning | 1 | 0
0 | 0
0 | 0
0 |
| scheduler | 1 | 0
0 | 0
0 | 0
0 |
| semantic | 0
0 | 0
0 | 0
0 | 0
0 |
| skill_matrix | 1 | 0
0 | 0
0 | 1 |
| tenant | 1 | 0
0 | 0
0 | 0
0 |
| workflow | 1 | 0
0 | 0
0 | 1 |
