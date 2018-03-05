/*--------------------------------------------------------------
# Copyright (C) joomla-monster.com
# License: http://www.gnu.org/licenses/gpl-2.0.html GNU/GPLv2 only
# Website: http://www.joomla-monster.com
# Support: info@joomla-monster.com
---------------------------------------------------------------*/

//Set Module's Height script

function setModulesHeight() {
	var regexp = new RegExp("_mod([0-9]+)$");

	var jmmodules = jQuery(document).find('.jm-module') || [];
	if (jmmodules.length) {
		jmmodules.each(function(index,element){
			var match = regexp.exec(element.className) || [];
			if (match.length > 1) {
				var modHeight = parseInt(match[1]);
				jQuery(element).find('.jm-module-in').css('min-height', modHeight + 'px');
			}
		});
	}
}

jQuery(document).ready(function(){
	
	setModulesHeight();

});

//search hide
jQuery(document).ready(function(){
	var djMenu = jQuery('#jm-top-bar');
	if (djMenu.length > 0) {
		
		var searchModule = djMenu.find('.search-ms');
		var searchModuleInput = djMenu.find('#mod-search-searchword');
		var searchModuleButton = searchModule.find('.button');

		if (searchModule.length > 0 && searchModuleButton.length > 0 ) {
	
	  		searchModuleButton.mouseover(function (event) {
	  	        searchModuleInput.addClass('show');
	  	        searchModuleInput.focus();  
	  	    }); 
	  	    
	        searchModuleInput.focusout(function() {
	  	    	searchModuleInput.removeClass('show');
	  	    });

		}
	}  
});

// Tabs
// Main tab on homepage resize so Tabs will have full width
function resizeTabs() {
	var modules = jQuery.find("div.full-tabs-ms");
  if (!modules.length) return;
	
	jQuery(modules).each(function(i,e) {
		var sWidth = "auto";
		var liTarget = jQuery(e).find(".tabs-wrapper .djtabs-title-wrapper");
		var liLength = liTarget.length;
		
		//Each tab will have proportional width only if window width is bigger then 767px
		if ((liLength > 0) && (jQuery(window).width() > 767)) {
			sWidth = (100 / liLength) + "%";
		}
		liTarget.width(sWidth);
	});
};

jQuery(document).ready(function () {
    resizeTabs();
    jQuery(window).resize(function() {
        resizeTabs();
    });
});





