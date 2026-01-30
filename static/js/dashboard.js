$(document).ready(function () {

    $('#sidebar-menu li').click(function () {

        // active state
        $('#sidebar-menu li').removeClass('active')
        $(this).addClass('active')

        // hide all sections
        $('.tab-content').hide()
        // $('#content').hide()

        // show selected
        let target = $(this).data('target')
        $('#' + target).show()
    })
    

    $('#sidebar-menu li[data-target="content"]').click(function() {
        $('.tab-content').hide()
        $('#content').show()
    })

    $('.view-edit-item').on('click', function() {
        let id = $(this).data('id');
        let name = $(this).data('name');
        let description = $(this).data('description');
        let price = $(this).data('price');
        $('#editItemId').val(id);
        $('#editItemName').val(name);
        $('#editItemDescription').val(description);
        $('#editItemPrice').val(price);
    });

    $('#viewEditItemForm').on('submit', function(e) {
        e.preventDefault();
        let formData = $(this).serialize();
        $.ajax({
            url: '/update_item', 
            method: 'POST',
            data: formData,
            success: function(response) {
                if(response.status === 'success') {                  
                    let row = $('#itemRow' + response.item.item_id);
                    row.find('.item-name').text(response.item.item_name);
                    row.find('.item-description').text(response.item.item_description);
                    row.find('.item-price').text(response.item.item_price);
                    $('#editItemName').val(response.item.item_name);
                    $('#editItemDescription').val(response.item.item_description);
                    $('#editItemPrice').val(response.item.item_price);
                    $('#viewEditItemModal').modal('hide');
                } else {
                    alert('Update failed!');
                }
            },
            error: function() {
                alert('Server error!');
            }
        });
    });

    $('.view-edit-location').on('click', function() {
        let location_id = $(this).data('location_id');
        let location_name = $(this).data('location_name');
        $('#editLocationId').val(location_id);
        $('#editLocationName').val(location_name);
    });

    $('#viewEditLocationForm').on('submit', function(e) {
        e.preventDefault();
        let formData = $(this).serialize()
        $.ajax({
            url: 'update_location',
            method: 'POST',
            data: formData,
            success: function(response) {
                if (response.status === 'success') {
                    let row = $('#locationRow' + response.location.location_id);
                    row.find('.location-name').text(response.location.location_name);
                    $('#editLocationName').val(response.location.location_name);
                   
                    $('#viewEditLocationModal').modal('hide');
                } else {
                    alert('Update failed!');
                }
            }, error: function(response) {
                alert('Server error!')
            }
        })

    })

    $('.view-edit-distance').on('click', function() {
        let distance_id = $(this).data('distance_id')
        let from_location = $(this).data('from_location')
        let to_location = $(this).data('to_location')
        let distance_in_km = $(this).data('distance_km')
        let distance_price = $(this).data('distance_price')

        $('#editDistanceId').val(distance_id);
        $('#editFromLocation').val(from_location);
        $('#editToLocation').val(to_location);
        $('#editDistanceInKm').val(distance_in_km);
        $('#editDistancePrice').val(distance_price);
    })

    $('#viewEditDistanceForm').on('submit', function(e) {
        e.preventDefault();
        let formData = $(this).serialize()
        $.ajax({
            url: '/update_distance',
            method: 'POST',
            data: formData,
            success: function(response) {
                if (response.status === 'success') {
                    let row = $('#distanceRow' + response.distance.distance_id);
                    row.find('.from_location').text(response.distance.from_location);
                    row.find('.to_location').text(response.distance.to_location);
                    row.find('.distance_km').text(response.distance.distance_km);
                    row.find('.distance_price').text(response.distance.price);

                    $('#editFromLocation').val(response.distance.from_location_id);
                    $('#editToLocation').val(response.distance.to_location_id);
                    $('#editDistanceInKm').val(response.distance.distance_km);
                    $('#editDistancePrice').val(response.distance.price);
                    
                   
                    $('#viewEditDistanceModal').modal('hide');
                } else {
                    alert('Update failed!');
                }
            }, error: function(response) {
                console.log('respnse error', response)
            }

        })




    })


    $("#addItemForm").on("submit", function (e) {
        e.preventDefault(); 
        $.ajax({
            url: "/add_item",
            type: "POST",
            data: $(this).serialize(),
            success: function (response) {
                if (response.status === "success") {
                    let row = `
                        <tr>
                            <td>${response.item.item_name}</td>
                            <td>${response.item.item_description}</td>
                            <td>${response.item.item_price}</td>
                            <td>
                                <button class="btn btn-info btn-sm view-edit-item"
                                    data-bs-toggle="modal"
                                    data-bs-target="#viewEditItemModal"
                                    data-id="${response.item.id}"
                                    data-name="${response.item.item_name}"
                                    data-description="${response.item.item_description}"
                                    data-price="${response.item.item_price}">
                                    View/Edit
                                </button>
                            </td>
                        </tr>
                    `;

                    $("#itemsTable tbody").append(row);

                    $("#addItemModal").modal("hide");
                }
            },
            error: function () {
                 console.log('response error:')
                alert("Something went wrong!");
            }
        });
    });

    var table = $('#itemsTable').DataTable();
    $("#itemsTable").on("click", '.delete-item', function () {
        let item_id = $(this).data('id')
        let row = $(this).closest('tr')

        console.log('item_id:', item_id)
        console.log('row:', row)

        if (!confirm('Are you sure you want to delete this item?')){
            return;
        }
        
        $.ajax({
            url: "/delete_item",
            type: "POST",
            data: { 'id': item_id},
            success: function(response) {
                console.log('response:', response)
                if (response.success) {
                    table.row(row).remove().draw(false)
                } else {
                    alert(response.message || 'Delete failed!')
                }
            }, error: function() {
                alert('server error')
            }
        })
    })

     $("#addLocationForm").on("submit", function (e) {
        e.preventDefault(); 
        $.ajax({
            url: "/add_location",
            type: "POST",
            data: $(this).serialize(),
            success: function (response) {
                if (response.status === "success") {
                    let row = `
                        <tr>
                            <td>${response.location.location_name}</td>
                            <td>
                                <button class="btn btn-info btn-sm view-edit-location"
                                    data-bs-toggle="modal"
                                    data-bs-target="#viewEditLocationModal"
                                    data-location_id="{{ location.location_id }}"
                                    data-location_name="{{ location.location_name }}" >
                                    View/Edit
                                </button>
                            </td>
                        </tr>
                    `;

                    $("#locationsTable tbody").append(row);

                    $("#addLocationModal").modal("hide");
                }
            },
            error: function () {
                 console.log('response error:')
                alert("Something went wrong!");
            }
        });
    });

    // var table = $('#locationsTable').DataTable();
    $("#locationsTable").on("click", '.delete-location', function () {
        let location_id = $(this).data('id')
        let row = $(this).closest('tr')

        console.log('item_id:', location_id)
        console.log('row:', row)

        if (!confirm('Are you sure you want to delete this item?')){
            return;
        }
        
        $.ajax({
            url: "/delete_location",
            type: "POST",
            data: { 'id': location_id},
            success: function(response) {
                console.log('response:', response)
                if (response.success) {
                    table.row(row).remove().draw(false)
                } else {
                    alert(response.message || 'Delete failed!')
                }
            }, error: function() {
                alert('server error')
            }
        })
    })
    


})