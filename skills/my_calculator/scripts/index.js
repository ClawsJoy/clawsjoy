/**

自定义计算器技能
*/

function execute(params) {
const a = params.a || 0;
const b = params.b || 0;
const op = params.op || 'add';

let result;
switch(op) {
case 'add':
result = a + b;
break;
case 'sub':
result = a - b;
break;
case 'mul':
result = a * b;
break;
case 'div':
if (b === 0) return { error: "除数不能为0" };
result = a / b;
break;
default:
result = a + b;
}

return { result, skill: "my-calculator" };
}

function getHelp() {
return "计算器指令格式：a=数字 b=数字 op=add/sub/mul/div";
}

module.exports = { execute, getHelp };
