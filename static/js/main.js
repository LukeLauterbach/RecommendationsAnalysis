function deleteItem(button) {
    var itemId = button.getAttribute("data-id");
    fetch('/delete_item/' + itemId, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function (response) {
        location.reload();
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Function to format the average rating
    function formatAverageRating(rating) {
        // Check if rating is an integer
        if (Number.isInteger(rating)) {
            return rating; // Return string for round numbers
        } else {
            // Return the first digit after the decimal point
            const [integerPart, decimalPart] = rating.toFixed(2).split('.');
            return `${integerPart}.${decimalPart.charAt(0)}`;
        }
    }

    // Process each average rating cell
    document.querySelectorAll('.average-rating').forEach(function(cell) {
        const rating = parseFloat(cell.textContent);
        cell.textContent = formatAverageRating(rating);
    });
});

$(document).ready(function () {
        // Handle form submission
        $('#new-entry-form').on('submit', function(e) {
            e.preventDefault(); // Prevent the default form submission

            $.ajax({
                url: addNewEntryUrl, // Use the variable from the HTML
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    title: $('#title').val() || '', // Provide default value
                    type: $('#type').val() || 'TV', // Provide default value
                    description: $('#description').val() || '', // Provide default value
                    rating_alex: $('#rating_alex').val() || 0, // Default to 0
                    rating_luke: $('#rating_luke').val() || 0, // Default to 0
                    rating_greg: $('#rating_greg').val() || 0, // Default to 0
                    rating_zach: $('#rating_zach').val() || 0  // Default to 0
                }),
                success: function(response) {
                    var alertBox = $('#new-entry-alert');
                    if (response.status === 'success') {
                        alertBox.text('New entry added successfully!');
                        alertBox.removeClass().addClass('alert alert-success').slideDown().delay(3000).slideUp();

                        // Clear the form fields
                        $('#new-entry-form')[0].reset();

                        // Reload the table data
                        loadTableData();
                    } else {
                        alertBox.text('Error adding entry: ' + response.message);
                        alertBox.removeClass().addClass('alert alert-error').slideDown().delay(3000).slideUp();
                    }
                },
                error: function() {
                    var alertBox = $('#new-entry-alert');
                    alertBox.text('An error occurred while adding the entry.');
                    alertBox.removeClass().addClass('alert alert-error').slideDown().delay(3000).slideUp();
                }
            });
        });

        $(document).on("focusout", ".description-input", function(e) {
            let updatedDescription = $(this).val();
            let itemId = $(this).data('item-id')

            $.ajax({
                url: '/update_description',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    item_id: itemId,
                    description: updatedDescription
                }),
                success: function(response) {
                    console.log(response);
                    // Handle success action here...
                },
                error: function(response) {
                    console.error('Error:', response);
                    // Handle error action here...
                }
            });
        });

        $(document).on("focusout", ".imdb_id-input", function(e) {
            let updatedIMDb = $(this).val();
            let itemId = $(this).data('item-id')

            $.ajax({
                url: '/update_imdb_id',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    item_id: itemId,
                    imdb_id: updatedIMDb
                }),
                success: function(response) {
                    console.log(response);
                    // Handle success action here...
                },
                error: function(response) {
                    console.error('Error:', response);
                    // Handle error action here...
                }
            });
        });

        function loadTableData() {
            $.ajax({
                url: getItemsUrl,
                type: "GET",
                success: function(response) {
                    if (response.status === 'success') {
                        var tableBody = $('#items-table tbody');
                        tableBody.empty(); // Clear the table body

                        response.items.forEach(function(item) {
                            var row = `<tr class="item-row" data-item-id="${item.id}">
                                <td><span class="item-name" style="cursor: pointer; color: #4CAF50;">${item.title}</span></td>
                                <td><input type="number" value="${item.rating_alex}" data-item-id="${item.id}" data-rating-type="alex" class="rating-input"></td>
                                <td><input type="number" value="${item.rating_greg}" data-item-id="${item.id}" data-rating-type="greg" class="rating-input"></td>
                                <td><input type="number" value="${item.rating_luke}" data-item-id="${item.id}" data-rating-type="luke" class="rating-input"></td>
                                <td><input type="number" value="${item.rating_zach}" data-item-id="${item.id}" data-rating-type="zach" class="rating-input"></td>
                                <td>${item.rating_average || 'N/A'}</td>
                            </tr>
                            <tr class="item-details" id="details-${item.id}" style="display: none;">
                                <td colspan="6"></td>
                            </tr>`;
                            tableBody.append(row);
                        });

                        // Re-apply the color function
                        $('.rating-input').each(function () {
                            setColor($(this));
                        });
                    } else {
                        console.error('Failed to load table data:', response.message);
                    }
                },
                error: function() {
                    console.error('Failed to load table data.');
                }
            });
        }

        // Load table data on page load
        loadTableData();

        // Update rating color
        function setColor(input) {
            var value = parseFloat(input.val()) || 0;  // Handle empty values
            var min = 1;
            var max = 10;
            var percentage = (value - min) / (max - min);

            // Ensure percentage is between 0 and 1
            percentage = Math.max(0, Math.min(1, percentage));

            var red = Math.round(255 * (1 - percentage));
            var green = Math.round(255 * percentage);
            var color = `rgb(${red}, ${green}, 0)`;

            // Apply background color
            input.css('background-color', value ? color : '#fff'); // White for empty values
        }

        // Apply color to all inputs initially
        $('.rating-input').each(function () {
            setColor($(this));
        });

        // Update color when input value changes
        $(document).on('input', '.rating-input', function () {
            setColor($(this));
        });

        $(document).on('input', '.rating-input', function() {
            var $input = $(this);
            var item_id = $input.data('item-id');
            var rating_type = $input.data('rating-type');
            var rating_value = $input.val();

            $.ajax({
                url: updateRatingUrl,
                type: "POST",
                contentType: "application/json",
                data: JSON.stringify({
                    item_id: item_id,
                    rating_type: rating_type,
                    rating_value: rating_value
                }),
                success: function(response) {
                    if (response.status === 'success') {
                        // Update average rating in the table
                        var $row = $('tr[data-item-id="' + item_id + '"]');
                        var $inputs = $row.find('.rating-input');
                        var totalRating = 0;
                        var numRatings = 0;

                        $inputs.each(function() {
                            var value = parseFloat($(this).val());
                            if (!isNaN(value) && value > 0) {
                                totalRating += value;
                                numRatings++;
                            }
                        });

                        var newAverage = numRatings > 0 ? (totalRating / numRatings) : 0;
                        $row.find('td').eq(5).text(newAverage.toFixed(1));  // Assuming the average rating is in the 6th column
                    } else {
                        console.error('Error updating rating:', response.message);
                    }
                },
                error: function() {
                    console.error('An error occurred while updating the rating.');
                }
            });
        });

        function updateAverageRating(itemId, newAverage) {
            var row = $('tr.item-row[data-item-id="' + itemId + '"]');
            row.find('td:eq(5)').text(newAverage || 'N/A');
        }


        // Event delegation for item details
        $(document).on('click', '.item-name', function () {
            var item_id = $(this).closest('.item-row').data('item-id');
            var detailsRow = $('#details-' + item_id);
            var detailsCell = detailsRow.find('td');

            if (detailsRow.is(':visible')) {
                detailsRow.slideUp();
            } else {
                $.ajax({
                    url: "/get_item_details/" + item_id,
                    type: "GET",
                    success: function (data) {
                        if (data.status !== 'error') {
                            let formattedBoxOffice = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0 }).format(data.box_office);
                            detailsCell.html(
                                '<table>' +
                                    '<tr data-item-id="' + item_id + '">' +
                                        '<td style="padding: 0; border: none; width: 1px; white-space: nowrap;" rowspan="7"><img src="' + data.poster + '"></td>' +
                                    '</tr>' +
                                    '<tr>' +
                                        '<td><strong>Description</strong></td>' +
                                        '<td><textarea data-item-id="' + item_id + '" class="description-input">' + data.description + '</textarea></td>' +
                                    '</tr>' +
                                    '<tr>' +
                                        '<td style="width: 1px; white-space: nowrap;"><strong>IMDb ID</strong></td>' +
                                        '<td><input type="text" data-item-id="' + item_id + '" class="imdb_id-input" value="' + data.imdb_id + '"></td>' +
                                    '</tr>' +
                                    '<tr>' +
                                        '<td style="width: 1px; white-space: nowrap;"><strong>IMDb Rating</strong></td>' +
                                        '<td>' + data.rating_imdb + '</td>' +
                                    '</tr>'+
                                        '<tr>' +
                                        '<td style="width: 1px; white-space: nowrap;"><strong>Genre</strong></td>' +
                                        '<td>' + data.genre + '</td>' +
                                    '</tr>' +
                                        '<tr>' +
                                        '<td style="width: 1px; white-space: nowrap;"><strong>Box Office</strong></td>' +
                                        '<td>' + formattedBoxOffice + '</td>' +
                                    '</tr>' +
                                    '<tr>' +
                                        '<td colspan="2"><button onclick="deleteItem(this);" data-id="' + item_id + '" class="btn btn-danger">Delete</button></td>' +
                                    '</tr>' +
                                '</table>'
                            );
                            detailsRow.slideDown();
                        } else {
                            detailsCell.html('<p>Error loading details.</p>');
                            detailsRow.slideDown();
                        }
                    },
                    error: function() {
                        detailsCell.html('<p>Error loading details.</p>');
                        detailsRow.slideDown();
                    }
                });
            }
        });
    });

$(document).ready(function () {
    // Sorting functionality
    $('.sortable').on('click', function () {
        var column = $(this).data('sort');
        var index = $(this).index();
        var isAscending = $(this).hasClass('asc');
        var rows = $('#items-table tbody tr.item-row').get();

        rows.sort(function (a, b) {
            var A, B;

            // Ensure the column index matches correctly
            if (column === 'rating_average') {
                A = parseFloat($(a).find('td').eq(index).text().trim()) || 0;
                B = parseFloat($(b).find('td').eq(index).text().trim()) || 0;
            } else if (column.startsWith('rating')) {
                A = parseFloat($(a).find('td').eq(index).find('input').val()) || 0;
                B = parseFloat($(b).find('td').eq(index).find('input').val()) || 0;
            } else {
                A = $(a).find('td').eq(index).text();
                B = $(b).find('td').eq(index).text();
            }

            // Handle sorting
            if (A < B) return isAscending ? -1 : 1;
            if (A > B) return isAscending ? 1 : -1;
            return 0;
        });

        // Reorder rows
        $.each(rows, function (index, row) {
            $('#items-table').children('tbody').append(row);
        });

        // Toggle sort direction
        $('.sortable').removeClass('asc desc');
        $(this).addClass(isAscending ? 'desc' : 'asc');
    });

    // Initial sort: Title column (index 0) in ascending order
    sortTableByColumn('items-table', 0, true);
});
