// Main JavaScript for Yarl IT Hub Coordinator Management System

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Task status update functionality
    $('.task-status-update').on('change', function() {
        var taskId = $(this).data('task-id');
        var newStatus = $(this).val();
        var progressBar = $(this).closest('.card').find('.progress-bar');
        var progressInput = $(this).closest('.card').find('.progress-input');
        
        // Update progress based on status
        var progress = 0;
        switch(newStatus) {
            case 'not_started':
                progress = 0;
                break;
            case 'in_progress':
                progress = 50;
                break;
            case 'completed':
                progress = 100;
                break;
            case 'on_hold':
                progress = 25;
                break;
        }
        
        // Update progress bar
        progressBar.css('width', progress + '%');
        progressBar.attr('aria-valuenow', progress);
        progressInput.val(progress);
        
        // Send AJAX request
        $.ajax({
            url: '/tasks/' + taskId + '/update-status/',
            method: 'POST',
            data: {
                'status': newStatus,
                'progress': progress,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    showAlert('Task status updated successfully!', 'success');
                    updateTaskCard(taskId, newStatus, progress);
                } else {
                    showAlert('Failed to update task status.', 'danger');
                }
            },
            error: function() {
                showAlert('Error updating task status.', 'danger');
            }
        });
    });

    // Progress bar update
    $('.progress-input').on('input', function() {
        var progress = $(this).val();
        var progressBar = $(this).closest('.card').find('.progress-bar');
        progressBar.css('width', progress + '%');
        progressBar.attr('aria-valuenow', progress);
    });

    // Filter functionality
    $('.filter-form select').on('change', function() {
        $(this).closest('form').submit();
    });

    // Search functionality
    $('.search-input').on('keyup', function() {
        var searchTerm = $(this).val().toLowerCase();
        var table = $(this).closest('.container').find('table');
        
        table.find('tbody tr').each(function() {
            var text = $(this).text().toLowerCase();
            if (text.indexOf(searchTerm) === -1) {
                $(this).hide();
            } else {
                $(this).show();
            }
        });
    });

    // Auto-refresh dashboard stats
    if ($('#dashboard-stats').length) {
        setInterval(function() {
            refreshDashboardStats();
        }, 30000); // Refresh every 30 seconds
    }

    // Document preview
    $('.document-preview').on('click', function() {
        var fileUrl = $(this).data('file-url');
        var fileName = $(this).data('file-name');
        
        // Create modal for document preview
        var modal = `
            <div class="modal fade" id="documentModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${fileName}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <iframe src="${fileUrl}" width="100%" height="500px"></iframe>
                        </div>
                        <div class="modal-footer">
                            <a href="${fileUrl}" class="btn btn-primary" download>Download</a>
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        $('body').append(modal);
        $('#documentModal').modal('show');
        
        $('#documentModal').on('hidden.bs.modal', function() {
            $(this).remove();
        });
    });

    // Form validation
    $('form').on('submit', function() {
        var isValid = true;
        
        $(this).find('[required]').each(function() {
            if (!$(this).val()) {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (!isValid) {
            showAlert('Please fill in all required fields.', 'warning');
            return false;
        }
    });

    // Remove invalid class on input
    $('input, select, textarea').on('input change', function() {
        if ($(this).val()) {
            $(this).removeClass('is-invalid');
        }
    });

    // Confirm delete actions
    $('.delete-confirm').on('click', function(e) {
        if (!confirm('Are you sure you want to delete this item?')) {
            e.preventDefault();
        }
    });

    // Auto-save forms
    $('form.auto-save input, form.auto-save textarea, form.auto-save select').on('change', function() {
        var form = $(this).closest('form');
        var formData = form.serialize();
        
        // Save to localStorage
        localStorage.setItem('form_' + form.attr('id'), formData);
        
        // Show auto-save indicator
        showAutoSaveIndicator();
    });

    // Load auto-saved form data
    $('form.auto-save').each(function() {
        var formId = $(this).attr('id');
        var savedData = localStorage.getItem('form_' + formId);
        
        if (savedData) {
            // Parse and populate form
            var params = new URLSearchParams(savedData);
            params.forEach(function(value, key) {
                var field = $('#' + key);
                if (field.length) {
                    field.val(value);
                }
            });
        }
    });

    // Clear auto-saved data on successful form submission
    $('form.auto-save').on('submit', function() {
        var formId = $(this).attr('id');
        localStorage.removeItem('form_' + formId);
    });
});

// Utility functions
function showAlert(message, type) {
    var alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    $('.container').first().prepend(alertHtml);
    
    // Auto-dismiss after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut();
    }, 5000);
}

function updateTaskCard(taskId, status, progress) {
    var card = $('[data-task-id="' + taskId + '"]').closest('.card');
    
    // Update status badge
    var statusBadge = card.find('.status-badge');
    statusBadge.removeClass().addClass('status-badge status-' + status.replace('_', '-'));
    statusBadge.text(status.replace('_', ' ').toUpperCase());
    
    // Update progress bar
    var progressBar = card.find('.progress-bar');
    progressBar.css('width', progress + '%');
    progressBar.attr('aria-valuenow', progress);
    
    // Update overdue indicator
    if (status === 'completed') {
        card.removeClass('overdue');
    }
}

function refreshDashboardStats() {
    $.ajax({
        url: '/api/dashboard-stats/',
        method: 'GET',
        success: function(data) {
            $('#total-initiatives').text(data.total_initiatives);
            $('#active-initiatives').text(data.active_initiatives);
            $('#total-tasks').text(data.total_tasks);
            $('#completed-tasks').text(data.completed_tasks);
            $('#overdue-tasks').text(data.overdue_tasks);
        }
    });
}

function showAutoSaveIndicator() {
    var indicator = $('#auto-save-indicator');
    if (indicator.length === 0) {
        indicator = $('<div id="auto-save-indicator" class="alert alert-info alert-dismissible fade show" style="position: fixed; top: 20px; right: 20px; z-index: 1050;">Auto-saved</div>');
        $('body').append(indicator);
    }
    
    indicator.fadeIn();
    
    setTimeout(function() {
        indicator.fadeOut();
    }, 2000);
}

// Export functionality
function exportToCSV(tableId, filename) {
    var table = document.getElementById(tableId);
    var csv = [];
    var rows = table.querySelectorAll('tr');
    
    for (var i = 0; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll('td, th');
        
        for (var j = 0; j < cols.length; j++) {
            var text = cols[j].innerText.replace(/"/g, '""');
            row.push('"' + text + '"');
        }
        
        csv.push(row.join(','));
    }
    
    var csvContent = csv.join('\n');
    var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    var link = document.createElement('a');
    
    if (link.download !== undefined) {
        var url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Print functionality
function printPage() {
    window.print();
}

// Date formatting
function formatDate(dateString) {
    var date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// File size formatting
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    var k = 1024;
    var sizes = ['Bytes', 'KB', 'MB', 'GB'];
    var i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
