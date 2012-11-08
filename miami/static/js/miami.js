function wrapTasks($tasks, $status, $accept, func_400) {
    $tasks.droppable({
        accept: $accept,
        activeClass: "ui-state-highlight",
        drop: function(event, ui) {
            $.ajax({
                type: 'PUT',
                url: '/tasks/' + $status + '/' + ui.draggable[0].id,
                success: function(data) {
                    var $item = ui.draggable;
                    $item.fadeOut(function() {
                        var $list = $("ul", $tasks).length ? $("ul", $tasks) : $("<ul class='ui-tasks-ul ui-helper-reset'/>").appendTo($tasks);
                        $item.appendTo($list).fadeIn();
                    });
                },
                statusCode: {
                    400: function(data) {
                        func_400(ui, data);
                    }
                },
                dataType: 'html'
            });
        }
    });

    $tasks.loadtasks = function() {
        $.ajax({
            type: 'GET',
            url: '/api/task',
            data: {
                q: '{"filters": [{"name": "status", "op": "eq", "val": "' + $status + '"}]}'
            },
            success: function(data) {
                var $list = $("ul", $tasks).length ? $("ul", $tasks) : $("<ul class='ui-tasks-ul ui-helper-reset'/>").appendTo($tasks);
                for(var i in data.objects) {
                    $('ul', $tasks).append('<li id="' + data.objects[i].id + '" class="ui-widget-content" style="display: list-item;"><h5>' + data.objects[i].title + '</h5><small>' + data.objects[i].status + '</small><p class="text-warning">$' + data.objects[i].price + '</p></li>');
                }

                $("li", $tasks).draggable({
                    cancel: "a.ui-icon",
                    // clicking an icon won't initiate dragging
                    revert: "invalid",
                    // when not dropped, the item will revert back to its initial position
                    containment: "document",
                    helper: "clone",
                    cursor: "move"
                });
            },
            dataType: 'json'
        });
    };
};