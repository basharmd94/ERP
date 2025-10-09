$(function () {
  var dt_ajax_table = $('.datatables-ajax');
  if (dt_ajax_table.length) {
    dt_ajax_table.DataTable({
      processing: true,
      serverSide: false,
      ajax: {
        url: '/crossapp/api/customers/',
        type: 'GET',
        dataSrc: 'customers',
        error: function (xhr, error, thrown) {
          console.error('Error loading customers:', error);
        }
      },
      columns: [
        { data: 'xcus', title: 'Customer Code' },
        { data: 'xshort', title: 'Customer Short Name' },
        { data: 'xstate', title: 'State' },
        { data: 'xcity', title: 'City' },
        { data: 'xmobile', title: 'Mobile' },
        { data: 'xemail', title: 'Email' },
        { data: 'xtaxnum', title: 'Tax Number' },
      ],
      dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6 d-flex justify-content-center justify-content-md-end"f>><"table-responsive"t><"row"<"col-sm-12 col-md-6"i><"col-sm-12 col-md-6"p>>',
      language: {
        processing: "Loading customers...",
        emptyTable: "No customers found",
        zeroRecords: "No matching customers found"
      }
    });
  }
});
