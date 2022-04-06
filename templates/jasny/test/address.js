$(function () {
	var $address = $('[name="address"]'),
		$parent = $('[name="parent"]');

	$address.fias({
		token: 'dkAFK4YehidrY7i9DHSY2DS4YidsreES',
		oneString: true,
        limit: 10,
		change: function (obj) {
			log(obj);
		},
        select: function() {
            $address.attr('disabled', 'disabled');
			$address.attr('value', $address.val());
			console.log($address.val());
        }
	});

	function log(obj) {
		var $log, i;

		$('.js-log li').hide();

		for (i in obj) {
			$log = $('#' + i);

			if ($log.length) {
				$log.find('.value').text(obj[i]);
				$log.show();
			}
		}
	}
	$("#renew-address").on('click', () => {
		$address.val('');
		$address.removeAttr('disabled');
	});
});