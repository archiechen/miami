$(function() {
  $('.nav li').removeClass('active');
  $(".nav li:nth-child(1)").addClass('active');
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

  var CurrentUser = Backbone.Model.extend({
    url: "/current_user",
    parse:function(response){
      return response.object;
    }
  });

  var current_user = new CurrentUser;


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
    gravatar_templ: _.template('<img src="http://gravatar.com/avatar/<%=gravater%>?s=20&amp;d=retro&amp;r=x" title="<%=name%>">'),
    events: {
      "click .btn-join": "join",
      "click .btn-leave": "leave",
      "dblclick .title": "edit",
      "keypress .edit"  : "updateOnEnter",
      "blur .edit"      : "close",
      "click #comments" : "show_detail"
    },
    initialize: function() {
      this.model.on('change', this.render, this);
      _.bindAll(this, 'edit');
      _.bindAll(this, 'show_detail');
    },
    join: function() {
      this.model.url = function() {
        return '/jointask/' + this.get('id');
      };
      this.model.save([], {
        success: function(model, response, options) {
          model.set({'partner':response.object.partner,'last_updated':response.object.last_updated});
        }
      });
    },
    leave: function() {
      this.model.url = function() {
        return '/leavetask/' + this.get('id');
      };
      this.model.save([], {
        success: function(model, response, options) {
          model.set({'partner':response.object.partner,'last_updated':response.object.last_updated});
        }
      });
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

    show_detail: function(){
      new BigTaskCard({model:this.model});
    },

    // If you hit `enter`, we're through editing the item.
    updateOnEnter: function(e) {
      if (e.keyCode == 13) this.close();
    },
    render: function() {
      var jsonModel = this.model.toJSON();
      this.$el.html(this.template(jsonModel));
      this.$el.attr('id', this.model.cid);
      if(jsonModel.owner.hasOwnProperty('name')) {
        this.$('#downright').append(this.gravatar_templ(jsonModel.owner));
      }
      if(jsonModel.partner.hasOwnProperty('name')) {
        this.$('#downright').append(this.gravatar_templ(jsonModel.partner));
        if(current_user.get('name') == jsonModel.partner.name) {
          this.$('#downright').append('<button class="btn btn-mini btn-leave" type="button">离开</button>');
        }
      } else {
        if(jsonModel.status == 'PROGRESS' && current_user.get('name') != jsonModel.owner.name) {
          this.$('#downright').append('<button class="btn btn-mini btn-join" type="button">加入</button>');
        }
      }

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

  var EstimatingForm = Backbone.View.extend({
    el: $('#modalForm'),
    templ: _.template($('#estimatingform-template').html()),
    events: {
      "click #save": "estimate"
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
    estimate: function(event) {
      this.model.url = function() {
        return '/estimate/' + this.get('id') + '/' + this.get('estimate');
      };
      var that = this;
      this.model.save('estimate', parseInt(this.$('#estimate').val()), {
        success: function(model, response, options) {
          that.$el.modal('hide');
          that.options.estimate_success(model, response, options);
        }
      });
    }
  });

  var BigTaskCard = Backbone.View.extend({
    el: $('#modalForm'),
    templ: _.template($('#bigtaskcard-template').html()),
    events: {
      "click #save": "save"
    },
    initialize: function() {
      var that = this;
      this.$el.on('hidden', function() {
        that.remove();
      });
      this.render();
      this.show();
    },
    save: function(event) {
      this.model.url = "/tasks";
      var that = this;
      this.model.save({detail: this.$('#detail').val()},{
        success: function(model, response, options) {
          that.$el.modal('hide');
          model.set({'detail':response.object.detail,'last_updated':response.object.last_updated});
        }
      });
    },
    render: function() {
      this.$el.html(this.templ(this.model.toJSON()));
      return this;
    },
    show: function() {
      this.$el.modal('show');
    }
  });

  var TaskForm = Backbone.View.extend({
    el: $('#modalForm'),
    templ: _.template($('#taskform-template').html()),
    category_templ: _.template('<li class="btn btn_category"><%=name%></li>'),
    events: {
      "click .btn_category": "selectCategory",
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
    pricingTask: function(event) {
      var that = this;
      var task = new Task({
        title: this.$('#title').val(),
        priority: this.$("#prioritySlider").slider("value"),
        categories: this.$('#tags').val(),
        status: 'READY',
        price: parseInt(event.target.value)
      });
      task.url = '/tasks';
      task.save([], {
        success: function(model, response, options) {
          that.options.tasks.add(response.object);
          that.options.tasks.sort();
          that.$el.modal('hide');
        }
      });
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
                return "/tasks/" + that.tasks.status + '/' + this.get('id');
              }
              var success_handle = function(model, response, options) {
                  ui.draggable.fadeOut(function() {
                    from.remove(draggableTask);
                    that.tasks.push(new Task(response.object));
                    that.tasks.sort();
                  });
                }
              draggableTask.save([], {
                success: success_handle,
                error: function(model, response, options) {
                  if(response.status == 400) {
                    var estimatingForm = new EstimatingForm({
                      model: model,
                      estimate_success: success_handle
                    });
                    estimatingForm.show();
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
      this.tasks_ul.empty();
      this.tasks.each(this.addOne);
    },

    render: function() {
      var total_price=0;
      this.tasks.each(function(task){
        total_price+=task.get('price');
      });
      this.$('#total_price').html(this.total_price_templ({price:total_price}));
      return this;
    },

    showTaskForm: function() {
      alert('禁用了:}');
      //var taskForm = new TaskForm({
      //  tasks: this.tasks
      //});
    }

  });


  var readyTaskList = new TaskList([], {
    status: 'READY'
  });

  var progressTaskList = new TaskList([], {
    status: 'PROGRESS'
  });

  var doneTaskList = new TaskList([], {
    status: 'DONE'
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
      readyTaskList.fetch({data: {team_id: event.target.name}});
      progressTaskList.fetch({data: {team_id: event.target.name}});
      doneTaskList.fetch({data: {team_id: event.target.name}});
    }

  });

  current_user.fetch({
    success: function() {
      var readyTasks = new TasksView({
        el: $("#rtasks"),
        from_task_lists: [progressTaskList, doneTaskList],
        accepts: "#ptasks li,#dtasks li",
        tasks: readyTaskList
      });

      var progressTasks = new TasksView({
        el: $("#ptasks"),
        from_task_lists: [readyTaskList, doneTaskList],
        accept: "#rtasks li,#dtasks li",
        tasks: progressTaskList
      });

      var doneTasks = new TasksView({
        el: $("#dtasks"),
        from_task_lists: [progressTaskList],
        accept: "#ptasks li",
        tasks: doneTaskList
      });

      new TeamSelectorView();
    }
  });
});