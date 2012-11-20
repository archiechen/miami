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
            make_join($target);
        }

        function make_join($target){
            $('.btn-join',$target).click(function(){
                var parent = $(this.parentElement.parentElement);
                $.ajax({
                    type: 'PUT',
                    url: '/jointask/' + parent.attr('id'),
                    success: function(data) {
                        parent.children().remove();
                        parent.append($(data).children());
                        make_join(parent);
                    },
                    dataType: 'html'
                });
            });
            $('.btn-leave',$target).click(function(){
                var parent = $(this.parentElement.parentElement);
                $.ajax({
                    type: 'PUT',
                    url: '/leavetask/' + parent.attr('id'),
                    success: function(data) {
                        parent.children().remove();
                        parent.append($(data).children());
                        make_join(parent);
                    },
                    dataType: 'html'
                });
            });
        }

        function moveto($item, $target, content) {
            $item.fadeOut(function() {
                var $list = $("ul", $target).length ? $("ul", $target) : $("<ul class='ui-helper-reset'/>").appendTo($target);
                $item.children().remove();
                $item.append($(content).children());
                $item.appendTo($list).fadeIn(function(){
                    make_join($item);
                });
            });
        }

        return {
            wrapTasks: wrapTasks,
            moveto: moveto
        }
    }());
}(jQuery));