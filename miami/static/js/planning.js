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
  var Team = Backbone.Model.extend({});

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

  var Teams = Backbone.Collection.extend({
    url: function() {
      return '/user/teams';
    },
    model: Team,
    parse: function(response) {
      return response.objects;
    }
  });

  var TaskCard = Backbone.View.extend({

    tagName: "li",
    className: "",

    template: _.template($('#taskcard-template').html()),

    events: {
      "dblclick .title": "edit",
      "keypress .edit"  : "updateOnEnter",
      "blur .edit"      : "close"
    },
    initialize: function() {
      this.model.on('change', this.render, this);
      _.bindAll(this, 'edit');
    },
    edit:function(){
      if(this.model.get('status')!='DONE'){
        this.$el.addClass('editing');
        this.title_input.focus();
      }
    },
    // Close the `"editing"` mode, saving changes to the todo.
    close: function() {
      if(this.title_input.val() != this.model.get('title')){
        this.model.url = '/tasks'
        this.model.save({title: this.title_input.val()},{
          success: function(model, response, options) {
            model.set({'title':response.object.title,'last_updated':response.object.last_updated});
          }
        });
      }
      this.$el.removeClass("editing");
    },

    // If you hit `enter`, we're through editing the item.
    updateOnEnter: function(e) {
      if (e.keyCode == 13) this.close();
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
      this.title_input = this.$('.edit');
      this.title_input.limit('33');
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
      /* Priority Slider */
      this.$("#prioritySlider").slider({
        range: "min",
        value: 5,
        min: 5,
        max: 100,
        step: 5,
        slide: function(event, ui) {
          that.$("#priorityAmount").text(ui.value);
        }
      });

      this.$("#priorityAmount").text(this.$("#prioritySlider").slider("value"));
    },
    get_team_id:function(){
      if(teamsView.current_team.attr('name')=='0'){
        return this.$('#selected_team_id').val();
      }else{
        return teamsView.current_team.attr('name');
      }
    },
    saveTask: function(task) {
      var that = this;
      var newTask
      if(task instanceof Task) {
        newTask = task;
      } else {
        newTask = new Task({
          title: this.$('#title').val(),
          detail:this.$('#detail').val(),
          team_id:this.get_team_id(),
          priority: this.$("#prioritySlider").slider("value"),
          categories: this.$('#tags').val(),
          status: 'NEW'
        });
      }
      newTask.url = '/tasks';
      newTask.save([], {
        success: function(model, response, options) {
          that.options.tasks.add(response.object);
          that.options.tasks.sort();
          that.$el.modal('hide');
        }
      });
    },
    pricingTask: function(event) {
      var task = new Task({
        title: this.$('#title').val(),
        detail:this.$('#detail').val(),
        team_id:this.get_team_id(),
        priority: this.$("#prioritySlider").slider("value"),
        categories: this.$('#tags').val(),
        status: 'NEW',
        price: parseInt(event.target.value)
      });
      this.saveTask(task);
    },
    selectCategory: function(event) {
      this.$('#tags').tagit('createTag', event.target.textContent);
    },
    addTeamSelector: function(){
      var team_selector = new TeamSelector();
      this.$('.modal-body').prepend(team_selector.$el);
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
      this.tasks.comparator = function(task) {
        return 100-task.get("priority");
      };
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
                    that.tasks.sort();
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
      if(teamsView.current_team.attr('name')=='0'){
        taskForm.addTeamSelector();
      }
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
      this.current_team.attr('name',event.target.name);
      newTaskList.fetch({data: {team_id: event.target.name}});
      readyTaskList.fetch({data: {team_id: event.target.name}});
    }

  });

  var TeamSelector = Backbone.View.extend({
    tagName:"select",
    id:"selected_team_id",
    templ:_.template('<option value="<%=id%>"><%=name%></option>'),
    initialize: function() {
      _.bindAll(this, 'addOne');
      this.teams = new Teams();
      this.teams.on('add', this.addOne, this);
      this.teams.on('reset', this.addAll, this);
      this.teams.on('all', this.render, this);
      this.teams.fetch();
    },
    addOne: function(team) {
      this.$el.append(this.templ(team.toJSON()));
    },

    addAll: function() {
      this.$el.empty();
      this.teams.each(this.addOne);
    },

    render: function() {
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

  var teamsView = new TeamSelectorView();

});