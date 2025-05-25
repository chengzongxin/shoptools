// 脚本语言：JScript (JavaScript for Applications)
function FillColumns_JSA() {
    console.log("fill jsa1");
    
    var app;
    try {
        app = Application;
    } catch (e) {
        try {
            app = this.Application;
        } catch (e) {
            try {
                app = new ActiveXObject("wps.Application");
            } catch (e) {
                alert("错误: 无法获取 WPS 应用对象，请确认在 WPS 宏环境中运行！");
                return;
            }
        }
    }

    if (!app) {
        alert("错误: 无法获取 WPS 应用对象！");
        return;
    }

    var sheet = app.ActiveWorkbook.ActiveSheet;
    
    // 解除工作表保护
    try {
        if (sheet.ProtectStatus) {
            sheet.Unprotect("");
            console.log("工作表保护已解除");
        }
    } catch (e) {
        console.log("警告: 解除保护失败，可能需要密码");
    }

    // 解锁A、B列
    sheet.Columns(1).Locked = false;
    sheet.Columns(2).Locked = false;

    // 定义映射字典（添加更多映射以覆盖可能的键）
    var dict = new Object();
    dict["CUSHION"] = "CU-0608";
    dict["Cushion"] = "CU-0608";

    dict["SLEEVE"] = "BE-0608";
    dict["Sleeve"] = "BE-0608";

    dict["SH"] = "SH-0608";
    dict["sh"] = "SH-0608";

    dict["CB"] = "CB-0608";
    dict["cb"] = "CB-0608";

    dict["Sock"] = "SO-0608";
    dict["sock"] = "SO-0608";

    dict["drawing"] = "CB-0608";
    dict["Drawing"] = "CB-0608";

    dict["Scarf"] = "BE-0608";
    dict["scarf"] = "BE-0608";

    dict["Apron"] = "AP-0608";
    dict["apron"] = "AP-0608";

    var lastRow = sheet
        .Range("D" + sheet.Rows.Count)
        .End(-4162)
        .Row;
    
    console.log("数据范围: 第2行至第" + lastRow + "行");
    
    // 分步执行并记录详细日志
    var errorCount = 0;
    for (var i = 2; i <= lastRow; i++) {
        try {
            // 获取D列和G列的实际值
            var dValue = sheet.Cells(i, 4).Value2;
            var gValue = sheet.Cells(i, 7).Value2;
            
            // 调试输出
            console.log(`第${i}行: D=${dValue}, G=${gValue}`);
            
            // 填充A列（直接使用值而非函数引用）
            sheet.Cells(i, 1).Value2 = dValue;
            
            // 处理G列内容
            var fullText = gValue + ""; // 确保转为字符串
            var key = fullText.split("_")[0] || "";
            
            // 调试输出分割结果
            console.log(`  分割结果: key="${key}"`);
            
            // 检查字典中是否存在该键（忽略大小写）
            var normalizedKey = key.trim();
            var matched = false;
            
            // 遍历字典查找匹配（忽略大小写）
            for (var dictKey in dict) {
                if (dictKey.toLowerCase() === normalizedKey.toLowerCase()) {
                    sheet.Cells(i, 2).Value2 = dict[dictKey];
                    console.log(`  B列填充: ${dict[dictKey]}`);
                    matched = true;
                    break;
                }
            }
            
            if (!matched) {
                sheet.Cells(i, 2).Value2 = "未定义";
                console.log("  B列未找到匹配项");
            }
            
            if (i % 50 === 0) {
                console.log("已处理: " + i + "/" + lastRow + "行");
            }
        } catch (e) {
            console.log("错误: 第" + i + "行处理失败 - " + e.message);
            errorCount++;
            
            if (errorCount > 10) {
                alert("错误过多，已停止处理。请检查日志。");
                break;
            }
        }
    }

    if (errorCount === 0) {
        alert("✅ A、B 列已成功填充完成！");
    } else {
        alert("⚠️ 填充过程中出现 " + errorCount + " 个错误，请查看WPS开发者工具日志。");
    }
}