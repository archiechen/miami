(function(jQuery) {
    jQuery.miami = (function() {
        function wrapTasks($tasks, $status, $accept, func_400) {
            $tasks.droppable({
                accept: $accept,
                activeClass: "ui-state-highlight",
                drop: function(event, ui) {
                    $.ajax({
                        type: 'PUT',
                        url: '/tasks/' + $status + '/' + ui.draggable[0].id,
                        success: function(data) {
                            moveto(ui.draggable, $tasks , data);
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
                            $('ul', $tasks).append('<li id="' + data.objects[i].id + '" style="display: list-item;">' + create_taskcard(data.objects[i]) + '</li>');
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

        function moveto($item, $target, $content) {
            $item.fadeOut(function() {
                var $list = $("ul", $target).length ? $("ul", $target) : $("<ul class='ui-helper-reset'/>").appendTo($target);
                $item.children().remove();
                $item.append($content);
                $item.appendTo($list).fadeIn();
            });
        }

        function create_taskcard(task) {
            return '<h5>' + task.title + '</h5><small>' + task.status + '</small><p class="text-warning">$' + task.price + '</p><p class="text-info">' + task.estimate + 'H</p><p class="text-info">' + task.consuming + 'S</p>';
        };

        return {
            wrapTasks:wrapTasks,
            moveto:moveto,
            create_taskcard:create_taskcard
        }
    }());
}(jQuery));