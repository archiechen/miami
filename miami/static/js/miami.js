function wrapTasks($tasks, $status, $accept) {
    $tasks.droppable({
        accept: $accept,
        activeClass: "ui-state-highlight",
        drop: function(event, ui) {
            $.ajax({
                type: 'PUT',
                url: '/api/task/' + ui.draggable[0].id,
                data: '{"status":"' + $status + '"}',
                success: function(data) {
                    var $item = ui.draggable;
                    $item.fadeOut(function() {
                        var $list = $("ul", $tasks).length ? $("ul", $tasks) : $("<ul class='ui-tasks-ul ui-helper-reset'/>").appendTo($tasks);

                        $item.appendTo($list).fadeIn();
                    });
                },
                dataType: 'json',
                contentType: 'application/json'
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
                    $('ul', $tasks).append('<li id="' + data.objects[i].id + '" class="ui-widget-content ui-corner-tr" style="display: list-item;"><a>' + data.objects[i].title + '</a><span>' + data.objects[i].status + '</span></li>');
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