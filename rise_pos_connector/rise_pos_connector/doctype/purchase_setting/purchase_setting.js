// Copyright (c) 2024, Huda Infoteh and contributors
// For license information, please see license.txt

frappe.ui.form.on('Purchase Setting', {
	refresh: function(frm) {
		// Add a custom button to trigger the API call
		frm.add_custom_button(__('Get All Purchases'), function() {

			frappe.call({
				method: 'rise_pos_connector.rise_pos_connector.doctype.purchase_setting.purchase_setting.get_shop_purchase_orders',
				args: {
				    shop_code: frm.doc.shop_code,
					api_key:frm.doc.api_key,
					auth_token:frm.doc.auth_token,
					only_special: frm.doc.only_special,
					limit: frm.doc.limit,
					page: frm.doc.page
				},
				callback: function(response) {
					frm.refresh();
				}
			});
		});
	}
	
});
