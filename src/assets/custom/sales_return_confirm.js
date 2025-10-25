
  processReturn = function() {
    // Show the confirmation dialog
    console.log("CLicked")
    // toast message
    toastr.success("Return processed successfully");
    console.log("hello world")
    // redirect to sales return list in new tab
    window.open("/sales/returns/", "_blank");

  }
