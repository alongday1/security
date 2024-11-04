function showDishes()
{

    const params = new URLSearchParams({
        canteen_id: '0',
        included_tags: null,
        excluded_tags: null,
        search_name: null,
    });

    // 发起 fetch 请求
    fetch(`${getDishesUrl}?${params.toString()}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('网络响应不成功');
            }
            return response.json(); // 转换为JSON
        })
        .then(data => {
            var dishHtml = '';
            if (canteenId === "0") {
                dishHtml = '<h2>全部菜品</h2>';
            } else {
                dishHtml = `<h2>${data.canteen_name}的菜品</h2>`;
            }

            // 遍历菜品并生成 HTML
            data.dishes.forEach(dish => {
                let url=`/comment?dish_id=${dish.id}`;
                console.log('url', url);
                dishHtml += `
                    <div class="dish-container" style="border: 1px solid #ddd; padding: 10px; margin-bottom: 15px;"
                         data-url="${url}">
                        <img src="${dish.image_url}" alt="${dish.name}" style="width: 150px; height: 100px; float: left; margin-right: 10px;">
                        <div style="overflow: hidden;">
                            <h4>{dish.name}</h4>
                            <p>描述：{dish.description}</p>
                            <p>食堂：{dish.canteen}</p>
                        </div>
                        <div style="clear: both;"></div>
                    </div>
                `;
            });

            document.getElementById('dish-content').innerHTML = dishHtml;

            // 为每个 dish-container 绑定点击事件，实现跳转
            document.querySelectorAll('.dish-container').forEach(container => {
                container.addEventListener('click', function() {
                    var url = this.getAttribute('data-url');
                    window.location.href = url;  // 跳转到菜品详情页面
                });
            });
        })
        .catch(error => {
            document.getElementById('dish-content').innerHTML = '<p>无法加载菜品，请稍后重试。</p>';
            console.error('Error fetching dishes:', error);
        });
}

// script.js
// 假设这是从服务器获取的数据，或者您可以将其替换为从localStorage等获取数据的逻辑
//dishes = Dish.objects.all()
//dishes_data = [{'id': dish.id, 'name': dish.name, 'description': dish.description, 'canteen': dish.canteen.name} for dish in dishes]


const items = [
    { id: 1, name: 'Item 1', type: 'Type A' },
    { id: 2, name: 'Item 2', type: 'Type B' },
    { id: 3, name: 'Item 3', type: 'Type B' },
];
// 初始化表格
function initTable() {
    const tableBody = document.getElementById('table-body');
    //tableBody.innerHTML = ''; // 清空表格内容
    items.forEach((item, index) => {

            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.type}</td>
            `;
            tableBody.appendChild(row);

    });
}