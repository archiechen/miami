$(function() {
    var TaskView = Backbone.View.extend({

        el: $("#main-container"),

        events: {
            "click #saveTask": "save",
            "click #taskform-price button": "pricing"
        },

        initialize: function() {
            $('#title').val('');
            $('#title').limit('33', '#charsLeft');
            $('#detail').val('');
        },

        save: function(event) {
            $('#saveTask').attr('disabled', 'true');
            $.ajax({
                type: 'POST',
                url: '/tasks',
                data: '{"title":"' + $('#title').val() + '","detail":"' + $('#detail').val() + '","status":"' + $('#status').val() + '"}',
                success: this.options.success_handle,
                dataType: 'json',
                contentType: 'application/json'
            });
        },

        pricing: function(event) {
            $('#taskform-price button').attr('disabled', 'true');
            $.ajax({
                type: 'POST',
                url: '/tasks',
                data: '{"title":"' + $('#title').val() + '","detail":"' + $('#detail').val() + '","price":' + event.target.value + ',"status":"' + $('#status').val() + '"}',
                success: this.options.success_handle,
                dataType: 'json',
                contentType: 'application/json'
            });
        },

    });

    var taskView = new TaskView({
        success_handle: function() {
            location = location;
        }
    });
});