$(document).ready(function()
{
	$(".btn-inform").click(function()
	{
		var id = $(this).attr('index');
		$.getJSON("/api/get_counter_info/" + id, function(data)
	    {
	    	if(data.status_code == '200')
	    	{
	    		$('#modal_cname').text(data.name);
	    	}
	    });
	    $.getJSON("/api/get_pkz/" + id, function(data)
	    {
	    	$('#modal_setpkz').attr('index',id);
	    	if(data.status_code == '200')
	    	{
	    		for (var i = 0; i < data.info.length; i++) {
	    			$('#month_pkz').append('<tr><td>'+data.info[i].pokaz+'</td>'+
	    				'<td>'+data.info[i].month_name+'</td>'+
	    				'<td>'+data.info[i].pdate+'</td>'+
	    				'<td>'+data.info[i].person+'</td></tr>')
	    		}
	    	}
	    	else
	    	{
	    		$('#modal_pkz').text('Не найдено')
	    	}
	    });
		$("#pkzmodal").modal('show');
	});
});

$(document).on('click', '#counter', function()
{
    var id = $(this).attr('index');
    $.getJSON("/api/get_counter_info/" + id, function(data)
    {
    	if(data.status_code == '200')
    	{
    		$('#info').text('Прибор учета: ' + data.name);
    		$('#zn').text(data.zn);
    		$('#ust_date').text(data.ust_date);
    		$('#pov_date').text(data.pov_date);
    		$('#nextpov_date').text(data.nextpov_date);
    	}
    });
});

$(document).on('click', '#modal_setpkz', function()
{
    var id = $(this).attr('index');
    var newpkz = parseFloat($('#newpkz').val());
    if (newpkz < 0) { return alert('Ошибка ввода. Введено отрицательное число'); }
    if (isNaN(newpkz)) { return alert('Ошибка ввода'); }
    $.getJSON("/api/set_pkz/" + id + '/' + $('#pkz_month').val() + '/' + $('#newpkz').val(), function(data)
    {
    	if(data.status_code == '200')
    	{
    		$('#modal_setpkz').attr('disabled','disabled');
    		$('#modal_setpkz').text('Показания записаны!');
    	}
    	else
    	{
    		return alert('Ошибка записи показаний!');
    	}
    });
});

$(document).on('click', '#modal_close', function()
{
	window.location.reload();
});