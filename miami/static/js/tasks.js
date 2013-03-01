$(function() {
  $('.nav li').removeClass('active');
  $(".nav li:nth-child(2)").addClass('active');
  var Task = Backbone.Model.extend({
    defaults: function() {
      return {
        price: 0,
        estimate: 0,
        detail: ''
      };
    },

    initialize: function() {
      if (!this.get("price")) {
        this.set({
          "price": this.defaults().price
        });
      }
      if (!this.get("estimate")) {
        this.set({
          "estimate": this.defaults().estimate
        });
      }
      if (!this.get("detail")) {
        this.set({
          "detail": this.defaults().detail
        });
      }
    }
  });

  var Category = Backbone.Model.extend({});
  var CategoryList = Backbone.Collection.extend({
    url: function() {
      return '/categories';
    },
    model: Category,
    parse: function(response) {
      return response.objects;
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
      this.categories.fetch();
    },
    saveTask: function(task) {
      var that = this;
      var newTask
      if (task instanceof Task) {
        newTask = task;
      } else {
        newTask = new Task({
          title: this.$('#title').val(),
          priority: this.$("#prioritySlider").slider("value"),
          categories: this.$('#tags').val(),
          status: 'NEW'
        });
      }
      newTask.url = '/tasks';
      newTask.save([], {
        success: function() {
          location = location;
        }
      });
    },
    pricingTask: function(event) {
      var task = new Task({
        title: this.$('#title').val(),
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
    }
  });

  var taskForm = new TaskForm;

  /* Priority Slider */
  $("#prioritySlider").slider({
    range: "min",
    value: 5,
    min: 5,
    max: 100,
    step: 5,
    slide: function(event, ui) {
      $("#priorityAmount").text(ui.value);
    }
  });

  $("#priorityAmount").text($("#prioritySlider").slider("value"));

});