(function() {
    // Initial Setup
    // -------------
    // Save a reference to the global object (`window` in the browser, `exports`
    // on the server).
    var root = this;

    // Save the previous value of the `Backbone` variable, so that it can be
    // restored later on, if `noConflict` is used.
    var previousMiami = root.Miami;

    // The top-level namespace. All public Miami classes and modules will
    // be attached to this. Exported for both CommonJS and the browser.
    var Miami;
    if(typeof exports !== 'undefined') {
        Miami = exports;
    } else {
        Miami = root.Miami = {};
    }

    // Require Underscore, if we're on the server, and it's not already present.
    var _ = root._;
    if(!_ && (typeof require !== 'undefined')) _ = require('underscore');

    // For Miami's purposes, jQuery, Zepto, or Ender owns the `$` variable.
    Miami.$ = root.jQuery || root.Zepto || root.ender;

    // Runs Miami.js in *noConflict* mode, returning the `Miami` variable
    // to its previous owner. Returns a reference to this Miami object.
    Miami.noConflict = function() {
        root.Miami = previousMiami;
        return this;
    };

    var views = Miami.views = {};
    Miami.views.TaskForm = Backbone.View.extend({

        el: $("#taskForm"),

        events: {
            "click #saveTask": "save",
            "click #taskform-price button": "pricing"
        },

        initialize: function() {
            $('#title').val('');
            $('#title').limit('33', '#charsLeft');
            $('#detail').val('');
            $('#saveTask').removeAttr('disabled');
            $('#taskform-price button').removeAttr('disabled')
        },

        save: function(event) {
            $('#saveTask').attr('disabled', 'true');
            $('#taskform-price button').attr('disabled', 'true')
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


}).call(this);