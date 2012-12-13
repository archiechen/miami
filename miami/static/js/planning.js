$(function() {

  var Task = Backbone.Model.extend({});

  var TaskList = Backbone.Collection.extend({
    initialize: function(models, options) {
      this.status = options.status;
    },
    url: function() {
      return '/api/task?q={"filters": [{"name": "status", "op": "eq", "val": "' + this.status + '"}]}';
    },
    model: Task,
    parse: function(response) {
      return response.objects;
    }
  });

  var TaskCard = Backbone.View.extend({

    tagName: "li",
    className: "",

    template: _.template($('#taskcard-template').html()),

    initialize: function() {
      this.model.on('change', this.render, this);
    },

    render: function() {
      this.$el.html(this.template(this.model.toJSON()));
      this.$el.attr('id', this.model.cid);
      this.$el.draggable({
        cancel: "a.ui-icon",
        revert: "invalid",
        containment: "document",
        helper: "clone",
        cursor: "move"
      });
      return this;
    }
  });

  var PricingForm = Backbone.View.extend({
    el: $('#priceForm'),
    templ: _.template($('#pricingform-template').html()),
    events: {
      "click .btn": "pricing"
    },
    initialize: function() {
      this.render();
    },
    render: function() {
      this.$el.html(this.templ(this.model.toJSON()));
      return this;
    },
    show: function() {
      this.$el.modal('show');
    },
    pricing: function(event) {
      this.model.url = function() {
        return '/pricing/' + this.get('id') + '/' + this.get('price');
      };
      var that = this;
      this.model.save('price', parseInt(event.target.value), {
        success: function() {
          that.$el.modal('hide');
          that.remove();
          that.options.price_success();
        }
      });
    }
  });

  var newTaskList = new TaskList([], {
    status: 'NEW'
  });

  var readyTaskList = new TaskList([], {
    status: 'READY'
  });

  var TasksView = Backbone.View.extend({

    initialize: function() {
      _.bindAll(this, 'addAll', 'addOne');
      var that = this;
      this.tasks_ul = this.$('#taskcard_list');
      this.tasks = this.options.tasks;
      this.from_task_lists = this.options.from_task_lists;
      this.tasks.on('add', this.addOne, this);
      this.tasks.on('reset', this.addAll, this);
      this.tasks.fetch();
      this.$el.droppable({
        accept: this.options.accept,
        activeClass: "ui-state-highlight",
        drop: function(event, ui) {
          var cid = $(ui.draggable).attr('id');
          _.each(that.from_task_lists, function(from) {
            var draggableTask = from.getByCid(cid);
            if(typeof draggableTask != 'undefined') {
              draggableTask.url = function() {
                return "/tasks/" + this.get('status') + '/' + this.get('id');
              }
              var success_handle = function() {
                  ui.draggable.fadeOut(function() {
                    from.remove(draggableTask);
                    that.tasks.push(draggableTask);
                  });
                }
              draggableTask.save('status', that.tasks.status, {
                success: success_handle,
                error: function(model, response, options) {
                  if(response.status == 400) {
                    var pricingForm = new PricingForm({
                      model: model,
                      price_success: success_handle
                    });
                    pricingForm.show();
                  }
                  if(response.status == 401) {
                    alert('unauthorization');
                  }
                  if(response.status == 403) {
                    alert('已经有任务了');
                  }
                }
              });
            }
          });
        }
      });
    },

    addOne: function(task) {
      var view = new TaskCard({
        model: task
      });
      view.render().$el.appendTo(this.tasks_ul).fadeIn();
    },

    addAll: function() {
      this.tasks.each(this.addOne);
    },

    render: function() {
      console.log('tasks view render.');
      return this;
    }

  });

  var newTasks = new TasksView({
    el: $("#ntasks"),
    from_task_lists: [readyTaskList],
    accept: "#rtasks li",
    tasks: newTaskList
  });

  var readyTasks = new TasksView({
    el: $("#rtasks"),
    from_task_lists: [newTaskList],
    accepts: "#ntasks li",
    tasks: readyTaskList
  });

});