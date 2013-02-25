$(function() {
  $('.nav li').removeClass('active');
  $(".nav li:nth-child(3)").addClass('active');
  var Task = Backbone.Model.extend({
    defaults: function() {
      return {
        price: 0,
        estimate: 0,
        detail: ''
      };
    },

    initialize: function() {
      if(!this.get("price")) {
        this.set({
          "price": this.defaults().price
        });
      }
      if(!this.get("estimate")) {
        this.set({
          "estimate": this.defaults().estimate
        });
      }
      if(!this.get("detail")) {
        this.set({
          "detail": this.defaults().detail
        });
      }
    }
  });
  var Category = Backbone.Model.extend({});

  var TaskList = Backbone.Collection.extend({
    initialize: function(models, options) {
      this.status = options.status;
    },
    url: function() {
      return '/tasks/' + this.status;
    },
    model: Task,
    parse: function(response) {
      return response.objects;
    }
  });

  var CategoryList = Backbone.Collection.extend({
    url: function() {
      return '/categories';
    },
    model: Category,
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
    el: $('#modalForm'),
    templ: _.template($('#pricingform-template').html()),
    events: {
      "click .btn": "pricing"
    },
    initialize: function() {
      var that = this;
      this.$el.on('hidden', function() {
        that.remove();
      });
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
          that.options.price_success();
        }
      });
    }
  });

  var TaskForm = Backbone.View.extend({
    el: $('#modalForm'),
    templ: _.template($('#taskform-template').html()),
    category_templ: _.template('<li class="btn btn_category"><%=name%></li>'),
    events: {
      "click .btn_category": "selectCategory",
      "click #saveTask": "saveTask",
      "click .btn_pricing": "pricingTask"
    },
    initialize: function() {
      _.bindAll(this, 'addAll');
      var that = this;
      this.$el.on('hidden', function() {
        that.remove();
      });
      this.categories = new CategoryList;
      this.categories.on('reset', this.addAll, this);
      this.render();
      this.categories.fetch({
        success: function() {
          that.show();
        }
      });
    },
    saveTask: function(task) {
      var that = this;
      var newTask
      if(task instanceof Task) {
        newTask = task;
      } else {
        newTask = new Task({
          title: this.$('#title').val(),
          categories: this.$('#tags').val(),
          status: 'NEW'
        });
      }
      newTask.url = '/tasks';
      newTask.save([], {
        success: function(model, response, options) {
          that.options.tasks.add(response.object);
          that.$el.modal('hide');
        }
      });
    },
    pricingTask: function(event) {
      var task = new Task({
        title: this.$('#title').val(),
        categories: this.$('#tags').val(),
        status: 'NEW',
        price: parseInt(event.target.value)
      });
      this.saveTask(task);
    },
    selectCategory: function(event) {
      this.$('#tags').tagit('createTag', event.target.textContent);
    },
    addAll: function() {
      var that = this;
      this.categories.each(function(category) {
        var li = that.category_templ(category.toJSON());
        that.$('#select_tags').append(li);
      });
    },
    render: function() {
      this.$el.html(this.templ());
      this.$('#title').limit('33', '#charsLeft');
      this.$('#tags').tagit({
        placeholderText: 'Custom Tags'
      });
      this.$('#tags').tagit('removeAll');
      return this;
    },
    show: function() {
      this.$el.modal('show');
    }
  });

  var newTaskList = new TaskList([], {
    status: 'NEW'
  });

  var readyTaskList = new TaskList([], {
    status: 'READY'
  });

  var TasksView = Backbone.View.extend({
    total_price_templ: _.template('<span class="badge badge-warning">$<%=price%></span>'),
    events: {
      "click #newtask_btn": "showTaskForm"
    },

    initialize: function() {
      _.bindAll(this, 'addAll', 'addOne');
      var that = this;
      this.tasks_ul = this.$('#taskcard_list');
      this.tasks = this.options.tasks;
      this.from_task_lists = this.options.from_task_lists;
      this.tasks.on('add', this.addOne, this);
      this.tasks.on('reset', this.addAll, this);
      this.tasks.on('all', this.render, this);
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
      this.tasks_ul.empty();
      this.tasks.each(this.addOne);
    },

    render: function() {
      var total_price = 0;
      this.tasks.each(function(task) {
        total_price += task.get('price');
      });
      this.$('#total_price').html(this.total_price_templ({
        price: total_price
      }));
      return this;
    },

    showTaskForm: function() {
      var taskForm = new TaskForm({
        tasks: this.tasks
      });
    }

  });

  var TeamSelectorView = Backbone.View.extend({
    el: $("#team_selector"),
    events: {
      "click li > a": "select"
    },
    initialize: function() {
      this.current_team = this.$("#current_team");
      _.bindAll(this, 'select');
    },
    select:function(event){
      this.current_team.text(event.target.text);
      newTaskList.fetch({data: {team_id: event.target.name}});
      readyTaskList.fetch({data: {team_id: event.target.name}});
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

  new TeamSelectorView();

});