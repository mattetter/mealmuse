$(document).ready(function() {
    $('.add-to-list, .add-to-pantry').click(function(event) {
      event.preventDefault();
      const name = /* Get item name */;
      const quantity = /* Get item quantity */;
      const list_type = $(this).hasClass('add-to-list') ? 'shopping_list' : 'pantry';
  
      $.post('/add_item', { name: name, quantity: quantity, list_type: list_type }, function(data) {
        // Handle response (e.g., update UI)
      });
    });
  });
  