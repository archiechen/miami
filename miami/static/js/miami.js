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
                            moveto(ui.draggable, $tasks, data);
                        },
                        statusCode: {
                            400: function(data) {
                                func_400(ui, data);
                            },
                            401: function(data) {
                                alert('unauthorization');
                            },
                            403: function(data) {
                                alert('已经有任务了');
                            }
                        },
                        dataType: 'html'
                    });
                }
            });

            $tasks.loadtasks = function() {
                $.ajax({
                    type: 'GET',
                    url: '/tasks/'+$status,
                    success: function(data) {
                        var $list = $("ul", $tasks).length ? $("ul", $tasks) : $("<ul class='ui-tasks-ul ui-helper-reset'/>").appendTo($tasks);
                        $('ul',$tasks).append(data);
                        make_draggable($tasks);
                    },
                    dataType: 'html'
                });
            };
        };

        function make_draggable($target){
            $("li", $target).draggable({
                cancel: "a.ui-icon",
                // clicking an icon won't initiate dragging
                revert: "invalid",
                // when not dropped, the item will revert back to its initial position
                containment: "document",
                helper: "clone",
                cursor: "move"
            });
        }

        function moveto($item, $target, content) {
            $item.fadeOut(function() {
                var $list = $("ul", $target).length ? $("ul", $target) : $("<ul class='ui-helper-reset'/>").appendTo($target);
                $item.children().remove();
                $item.append($(content).children());
                $item.appendTo($list).fadeIn();
                $('button',$item).click(function(){
                    alert('join')
                });
            });
        }

        function create_taskcard(task) {
            var consuming = 0;
            for(var i in task.time_slots) {
                consuming += task.time_slots[i].consuming;
            }
            var owner = '';
            if(task.owner != null) {
                owner = task.owner.name;
            }
            return '<h5>' + task.title + '</h5><small>' + task.status + '</small><p class="text-warning">$' + task.price + '</p><p class="text-info">' + task.estimate + 'H</p><p class="text-info">' + consuming + 'S</p><p class="text-info">' + owner + '</p>';
        };

        return {
            wrapTasks: wrapTasks,
            moveto: moveto,
            create_taskcard: create_taskcard
        }
    }());
}(jQuery));