$(function(){

  var Task = Backbone.Model.extend({

    defaults: function() {
      return {
        title: "empty todo...",
        status: "NEW",
        price : 0,
        estimate:0
      };
    }
  });

  var TaskList = Backbone.Collection.extend({

    model: Task,
    url:'/api/task',
    parse: function(response) {
        return response.objects;
    }
  });

  var Tasks = new TaskList;

  var TaskView = Backbone.View.extend({

    tagName:  "li",

    template: _.template($('#task-template').html()),

    events: {
      "click .join"   : "join",
      "click .leave"  : "leave"
    },

    initialize: function() {
      this.model.on('change', this.render, this);
    },

    render: function() {
      this.$el.html(this.template(this.model.toJSON()));
      return this;
    },

    join: function() {
      alert('join');
    },

    leave: function() {
      alert('leave');
    }

  });

  var TaskSlot = Backbone.View.extend({

    el: $("#ntasks"),

    initialize: function() {

      Tasks.on('add', this.addOne, this);
      Tasks.on('reset', this.addAll, this);
      Tasks.on('all', this.render, this);

      
      Tasks.fetch();
    },  

    render: function() {

     
    },

    addOne: function(task) {
      var view = new TaskView({model: task});
      this.$("#newTasks").append(view.render().el);
    },

    // Add all items in the **Todos** collection at once.
    addAll: function() {
      Tasks.each(this.addOne);
    }

  });

  // Finally, we kick things off by creating the **App**.
  var NewTaskSlot = new TaskSlot;

});
