require(['jquery', 'splunkjs/mvc/simplexml/ready!'], function($) {
    // Grab the DOM for the first dashboard row
    var firstRow = $('.dashboard-row').first();
    // Get the dashboard cells (which are the parent elements of the actual panels and define the panel size)
    var panelCells = $(firstRow).children('.dashboard-cell');
    // Adjust the cells' width
    $(panelCells[0]).css('width', '30%');
    $(panelCells[1]).css('width', '70%');
});