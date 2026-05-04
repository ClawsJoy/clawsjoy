import re
with open('task_api.py', 'r') as f:
    content = f.read()

old_method = r'def _handle_promo\(self\):.*?(?=\n    def \w|$)'
new_method = '''
    def _handle_promo(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            tenant_id = data.get('tenant_id', '1')
            city = data.get('city', '香港')
            style = data.get('style', '科技')
            source = data.get('source', 'auto')
            personal = get_library_images_by_tags(tenant_id, [city], limit=6)
            print(f"🔍 检索到个人图片数: {len(personal)}", flush=True)
            if source == 'library_only':
                final_images = personal[:6]
            elif source == 'external_only':
                final_images = fetch_external_images(city, style, 6)
            else:
                final_images = personal[:]
                if len(final_images) < 6:
                    needed = 6 - len(final_images)
                    final_images.extend(fetch_external_images(city, style, needed))
            if not final_images:
                self.send_json({'success': False, 'error': '没有可用图片素材'})
                return
            task_id = self._record_task(tenant_id, 'promo', {'city': city, 'style': style, 'source': source})
            self._deduct_balance(tenant_id, 0.01)
            video_name = f"{city}_{style}_{int(time.time())}.mp4"
            video_path = f"/home/flybo/clawsjoy/web/videos/{video_name}"
            first_img = final_images[0]
            cmd = f"ffmpeg -y -loop 1 -i '{first_img}' -c:v libx264 -t 15 -pix_fmt yuv420p -vf 'scale=1920:1080' '{video_path}'"
            subprocess.run(cmd, shell=True, stderr=subprocess.DEVNULL)
            self._update_task(task_id, 'completed', video_path)
            if os.path.exists(video_path):
                self.send_json({
                    'success': True,
                    'video_url': f"/videos/{video_name}",
                    'message': f'{city}{style}宣传片已生成',
                    'source': 'library' if personal else 'external',
                    'images_used': len(final_images)
                })
            else:
                self.send_json({'success': False, 'error': '视频合成失败'})
        except Exception as e:
            self.send_json({'success': False, 'error': str(e)}, 500)
'''

content = re.sub(old_method, new_method, content, flags=re.DOTALL)
with open('task_api.py', 'w') as f:
    f.write(content)
print("✅ _handle_promo 已替换")
