document.addEventListener('DOMContentLoaded', function() {
    const currentDateElement = document.getElementById('current-date');
    let currentDate = new Date(currentDateElement.innerText);



    // 初始化日期选择器
    flatpickr("#datepicker", {
        dateFormat: "Y-m-d",
        onChange: function(selectedDates) {
            // 选择日期后，重定向到新的日期（加一天）
            if (selectedDates.length > 0) {
                const newDate = new Date(selectedDates[0]);
                newDate.setDate(newDate.getDate() + 1); // 加一天
                window.location.href = `/record/?date=${newDate.toISOString().split('T')[0]}`;
            }
        }
    });

    document.getElementById('prev-date').addEventListener('click', function() {
        currentDate.setDate(currentDate.getDate() - 1);
        window.location.href = `/record/?date=${currentDate.toISOString().split('T')[0]}`;
    });

    document.getElementById('next-date').addEventListener('click', function() {
        currentDate.setDate(currentDate.getDate() + 1);
        window.location.href = `/record/?date=${currentDate.toISOString().split('T')[0]}`;
    });

    // 点击当前日期时，显示日期选择器
    currentDateElement.addEventListener('click', function() {
        document.getElementById('datepicker').click();
    });
});

document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', calculateCalories);
});
document.querySelectorAll('input[name="fruit"]').forEach(input => {
    input.addEventListener('change', calculateCalories);
})
function calculateCalories() {
    const genderInput = document.querySelector('input[name="fruit"]:checked'); // 获取选中的性别
    const age = parseInt(document.getElementById('age').value);
    const height = parseFloat(document.getElementById('height').value);
    const weight = parseFloat(document.getElementById('weight').value);

    // 确保所有输入都有效
    if (genderInput && age > 0 && age < 100 && height > 0 && weight > 0) {
        let bmr;
        const gender = genderInput.value; // 获取性别的值
        if (gender === 'male') {
            // 男性BMR公式
            bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
        } else {
            // 女性BMR公式
            bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
        }

        const maintainCalories = Math.round(bmr * 1.2); // 假设用户日常活动较少
        const loseCalories = Math.round(maintainCalories - 500); // 约减少500卡路里以减重

        document.getElementById('maintainCalories').innerText = `${maintainCalories} kcal`;
        document.getElementById('loseCalories').innerText = `${loseCalories} kcal`;
    } else {
        // 处理输入无效的情况
        document.getElementById('maintainCalories').innerText = '-';
        document.getElementById('loseCalories').innerText = '-';
    }
}




let currentPage = 1;  // 当前页码
let totalPages = 1;   // 总页数

function searchMeals() {
    const query = document.getElementById('search-input').value;
   
    

    // 如果搜索框为空，清空结果并隐藏分页
    if (!query.trim()) {
        document.getElementById('search-results').innerHTML = ''; // 清空结果
        document.getElementById('pagination').style.display = 'none'; // 隐藏分页
        
        return;
    }

    fetch(`/record/search/ajax/?search=${encodeURIComponent(query)}&page=${currentPage}`)
        .then(response => response.json())
        .then(data => {
           
            const searchResultsContainer = document.getElementById('search-results');
            searchResultsContainer.innerHTML = ''; // 清空当前内容
           
            const totalCountElement = document.getElementById('total-count');
            totalCountElement.innerHTML = `${data.total_count}个结果`  ;
            
            if (data.data.length === 0) {
                searchResultsContainer.innerHTML = '<p>没有找到记录。</p>';
                totalPages = 0;  // 如果没有记录，页数设置为 0
                updatePagination();
                return;
            }

            data.data.forEach(meal => {
                const mealItem = document.createElement('div');
                mealItem.className = 'ui brown segment'; // 确保这里是 "segment"
            
                mealItem.innerHTML = `
                    <div class="ui unstackable divided items">
                        <div class="item">
                            ${meal.image_url ? `
                                <a class="ui tiny image">
                                    <img style="margin-left:8%; margin-bottom:4%; margin-top:0;" src="${meal.image_url}" alt="meal image">
                                </a>
                            ` : ''}
            
                            ${meal.comment ? `
                                <div class="content" style="margin-left:1%; min-width:10em;">
                                    <div class="header">${meal.name} </div>
                                    <div class="meta">
                                     <span>${meal.meal_type_display}</span>
                                     <span> ${meal.created_at}</span>
                                    </div>
                                    <div class="description" style="margin-bottom:2%">
                                        <p><span class="ui small  text">${meal.comment}</span></p>
                                    </div>
                                </div>
                            ` : `
                                <div class="middle aligned content" style="margin-left:1%; min-width:10em;">
                                    <a class="header">${meal.name}</a>
                                     <div class="meta">
                                     <span>${meal.meal_type_display}</span>
                                     <span> ${meal.created_at}</span>
                                    </div>
                                </div>
                            `}
            
                            <div class="extra" style="display: flex; justify-content: flex-end;">
                                <span class="ui medium red text"><strong>${meal.calories}卡</strong></span>
                            </div>
                        </div>
                    </div>
                `;
            
                searchResultsContainer.appendChild(mealItem);
            });
            

            totalPages = Math.ceil(data.total_count / data.page_size); // 计算总页数
            updatePagination(); // 更新分页
        });
}

function updatePagination() {
    const paginationContainer = document.getElementById('pagination');
    const totalPagesDisplay = document.getElementById('total-pages');
    const pageCountDisplay = document.getElementById('page-count');
    const prevButton = document.getElementById('prev-button');
    const nextButton = document.getElementById('next-button');
    const pageInput = document.getElementById('page-input');
    const goButton = document.getElementById('go-button');

    // 更新总页数显示
    pageCountDisplay.innerText = totalPages;
    totalPagesDisplay.style.display = 'inline';

    // 只有在有搜索结果时显示分页
    if (totalPages > 0) {
        paginationContainer.style.display = 'flex';
    } else {
        paginationContainer.style.display = 'none';
        return;
    }

    // 上一页按钮
    prevButton.style.display = currentPage > 1 ? 'inline' : 'none';

    // 下一页按钮
    nextButton.style.display = currentPage < totalPages ? 'inline' : 'none';

    // 页码输入框和跳转按钮
    pageInput.style.display = 'inline';
    goButton.style.display = 'inline';
    pageInput.value = currentPage; // 设置当前页数
    pageInput.max=totalPages;

    // 跳转按钮事件
    goButton.onclick = () => {
        const newPage = parseInt(pageInput.value);
        if (newPage >= 1 && newPage <= totalPages) {
            currentPage = newPage;
            searchMeals();
        }
    };

    // 上一页按钮事件
    prevButton.onclick = () => {
        if (currentPage > 1) {
            currentPage--;
            searchMeals();
        }
    };

    // 下一页按钮事件
    nextButton.onclick = () => {
        if (currentPage < totalPages) {
            currentPage++;
            searchMeals();
        }
    };
}

document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('name');
    const calorieSuggestion = document.getElementById('calorie-suggestion');
    let per100gCalories = null;

    let debounceTimer;

    nameInput.addEventListener('input', async () => {
        clearTimeout(debounceTimer); // 清除上一次的定时器
        debounceTimer = setTimeout(async () => {
            const foodName = nameInput.value.trim();
            if (foodName) {
                let translatedFoodName = foodName;

                // 检测输入的语言（简单示例：检测是否有中文字符）
                if (/[\u4e00-\u9fa5]/.test(foodName)) {
                    // 如果是中文，则进行翻译
                    translatedFoodName = await translateToEnglish(foodName);
                }
                // 获取卡路里信息
                per100gCalories = await fetchCalories(translatedFoodName);
                // 显示或清除建议
                if (per100gCalories) {
                    calorieSuggestion.textContent = `建议：${foodName}每100克约含 ${per100gCalories} 卡路里`;
                } else {
                    calorieSuggestion.textContent = '';
                }
            } else {
                calorieSuggestion.textContent = ''; // 清除建议信息
            }
            console.log("请求的食物名称:", translatedFoodName);
        }, 300); // 设置防抖延时为300ms
    });
});

// 获取卡路里信息的函数
async function fetchCalories(foodName) {
    try {
        // 调试：打印食物名称
        console.log("请求的食物名称:", foodName);

        // Nutritionix API 配置
        const options = {
            method: 'POST',
            url: 'https://trackapi.nutritionix.com/v2/natural/nutrients',
            headers: {
                'Content-Type': 'application/json',
                'x-app-id': 'e59cdb5c', // 替换为你的 app id
                'x-app-key': '42da191aecce004ba07954fa3b05961f' // 替换为你的 app key
            },
            body: JSON.stringify({
                query: foodName
            })
        };

        // 发送请求
        const response = await fetch(options.url, {
            method: options.method,
            headers: options.headers,
            body: options.body
        });
        const data = await response.json();
        if (data.foods && data.foods.length > 0) {
            const foodItem = data.foods[0];
            // 获取卡路里数
            const calories = foodItem.nf_calories; // 使用 nf_calories 获取卡路里
            return calories; // 返回卡路里数
        } else {
            console.log("未找到相关食物数据。");
        }
    } catch (error) {
        console.error('获取卡路里数据时出错:', error);
    }
    return null;
}

// 修改后的 translateToEnglish 函数
async function translateToEnglish(foodName) {
    const API_KEY = '20241027002186585';
    const SECRET_KEY = '8ICrNzSMUVEYzlwtTCFs'; // 替换为你的密钥
    const URL = 'http://api.fanyi.baidu.com/api/trans/vip/translate';
    const salt = Date.now(); // 生成随机数

    // Step1: 拼接字符串1
    const sign = md5(`${API_KEY}${foodName}${salt}${SECRET_KEY}`);

    return new Promise((resolve, reject) => {
        // JSONP 请求
        $.ajax({
            url: URL,
            type: 'GET',
            dataType: 'jsonp', // 使用 jsonp
            data: {
                q: foodName,
                appid: API_KEY,
                salt: salt,
                from: 'zh', // 源语言为中文
                to: 'en',   // 目标语言为英语
                sign: sign
            },
            success: function (data) {
                if (data && data.trans_result) {
                    console.log('翻译结果:', data.trans_result[0].dst); // 输出翻译结果
                    resolve(data.trans_result[0].dst); // 返回翻译后的文本
                } else {
                    console.error('翻译失败:', data);
                    reject('翻译失败');
                }
            },
            error: function (xhr, status, error) {
                console.error('请求出错:', error);
                reject(error);
            }
        });
    });
}

// MD5 加密函数（可以使用现有的 md5 库或实现）
function md5(string) {
    return CryptoJS.MD5(string).toString(); // 使用 CryptoJS 库的 MD5 实现
}

function addNewImageInput(inputElement) {
    // 检查当前文件输入框是否已选择了文件
    if (inputElement.files.length > 0) {
        // 创建一个新的文件输入框
        const newInput = document.createElement('input');
        newInput.type = 'file';
        newInput.name = 'images';  // 保持名称相同，以便服务器接收多个文件
        newInput.accept = 'image/*';
        newInput.onchange = function() { addNewImageInput(newInput); };

        // 添加到文件上传容器中
        document.getElementById('image-upload-container').appendChild(newInput);
    }
}
