
jQuery(document).ready(function(){
	var obj = $('.navigation-down').find('div[_t_nav]');
	$.each(obj,function(index,val){
		var name = $(val).attr('_t_nav');
		$.get('/items/second',
			{
				alias:name
			},
			function(resp){
			$('#' + name).html(resp.tpl);
		});
	});

	var qcloud={};
	$('[_t_nav]').hover(function(){

		var _nav = $(this).attr('_t_nav');

		clearTimeout( qcloud[ _nav + '_timer' ] );

		qcloud[ _nav + '_timer' ] = setTimeout(function(){

		$('[_t_nav]').each(function(){

		$(this)[ _nav == $(this).attr('_t_nav') ? 'addClass':'removeClass' ]('nav-up-selected');

		});

		$('#'+_nav).stop(true,true).slideDown(200);

		}, 150);

	},function(){

		var _nav = $(this).attr('_t_nav');

		clearTimeout( qcloud[ _nav + '_timer' ] );

		qcloud[ _nav + '_timer' ] = setTimeout(function(){

		$('[_t_nav]').removeClass('nav-up-selected');

		$('#'+_nav).stop(true,true).slideUp(200);

		}, 150);

	});

});