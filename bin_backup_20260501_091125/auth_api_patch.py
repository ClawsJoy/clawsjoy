# 在 _handle_login 方法中，将错误返回替换为：

# 原代码：
# self.send_json({"success": False, "error": "用户名或密码错误"}, 401)

# 新代码：
# send_error(self, 401, "用户名或密码错误", 401)

# 在 _handle_register 方法中：
# send_error(self, 400, "邮箱必填", 400)

# 在 _handle_forgot 方法中：
# send_error(self, 404, "邮箱未注册", 404)
