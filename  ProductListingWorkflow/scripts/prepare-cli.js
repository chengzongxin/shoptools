const fs = require('fs');
const path = require('path');

// 读取编译后的 index.js
const indexContent = fs.readFileSync(path.join(__dirname, '../dist/index.js'), 'utf8');

// 创建 CLI 文件内容
const cliContent = `#!/usr/bin/env node

${indexContent}`;

// 写入 CLI 文件
fs.writeFileSync(path.join(__dirname, '../dist/cli.js'), cliContent);

// 设置执行权限
fs.chmodSync(path.join(__dirname, '../dist/cli.js'), '755'); 