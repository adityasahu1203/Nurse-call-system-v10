let lastEventIdentifier = null;
// Track if we are editing an existing bed
let isEditing = false;
let editingBedID = null;

// Function to fetch active calls and update the table
function fetchActiveCalls() {
    fetch('/active-calls')
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#activeCallsTable tbody');
            tableBody.innerHTML = '';

            data.forEach(call => {
                const row = document.createElement('tr');
                const callType = call.CALLTYPE.toLowerCase().replace(/\s+/g, '');
                const status = call.status.toLowerCase();

                // Determine the appropriate button image based on status and call type
                const buttonImage = status === 'a' ? '/static/images/acknowledge.gif' :
                    callType === 'normal' ? '/static/images/normal.gif' :
                    callType === 'emergency' ? '/static/images/emergency.gif' :
                    callType === 'codeblue' ? '/static/images/codeblue.gif' : '';

                // Construct the row with data
                row.innerHTML = `
                    <td>${call.WARD}</td>
                    <td>${call.ROOM_NO}</td>
                    <td>${call.BED_NO}</td>
                    <td>${call.CALLTYPE}</td>
                    <td>${call.CALL_AT}</td>
                    <td>
                        <button onclick="acknowledgeCall('${call.WARD}','${call.ROOM_NO}', '${call.BED_NO}', '${call.CALLTYPE}', '${call.CALL_AT}')">
                            <img src="${buttonImage}" alt="Acknowledge">
                        </button>
                    </td>
                `;
                row.setAttribute('data-calltype', callType);
                tableBody.appendChild(row);
            });

            // Update the last updated time
            document.getElementById('lastUpdated').textContent = new Date().toLocaleTimeString();
        })
        .catch(error => console.error('Error fetching call data:', error));
}

// Function to acknowledge a call
function acknowledgeCall(Ward, roomNo, bedNo, callType, callAt) {
    fetch('/acknowledge-call', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ WARD: Ward, ROOM_NO: roomNo, BED_NO: bedNo, CALL_TYPE: callType, CALL_AT: callAt })
    })
    .then(response => response.ok ? response.json() : Promise.reject('Failed to acknowledge call'))
    .then(data => {
        console.log('Call acknowledged:', data);
        fetchActiveCalls(); // Refresh the call list after acknowledgment
    })
    .catch(error => console.error('Error acknowledging call:', error));
}

// Initial load and periodic refresh every 5 seconds
fetchActiveCalls();
setInterval(fetchActiveCalls, 5000);

function displayFlashMessage(call) {
    const flashContainer = document.getElementById('flashMessages');

    if (!flashContainer) {
        console.error('Flash container not found');
        return;
    }

    const flashMessage = document.createElement('div');
    flashMessage.className = 'flash-message';

    flashMessage.innerHTML = `
        <strong>Room: ${call.ROOM_NO} | Bed: ${call.BED_NO} | Type: ${call.CALLTYPE}</strong>
    `;

    flashContainer.appendChild(flashMessage);

    setTimeout(() => {
        flashMessage.remove();
    }, 15000);
}

const eventSource = new EventSource('/stream-calls');

eventSource.onmessage = function(event) {
    const newEvent = JSON.parse(event.data);
    const eventIdentifier = `${newEvent.ROOM_NO}-${newEvent.BED_NO}-${newEvent.CALL_AT}`;

    if (eventIdentifier !== lastEventIdentifier) {
        displayFlashMessage(newEvent);
        lastEventIdentifier = eventIdentifier;
    }
};

document.addEventListener('DOMContentLoaded', function () {
    var modal = document.getElementById("loginModal");
    var btn = document.getElementById("loginButton");
    var span = document.getElementsByClassName("close")[0];

    if (btn && modal && span) {
        btn.onclick = function () {
            modal.style.display = "block";
        };

        span.onclick = function () {
            modal.style.display = "none";
        };

        window.onclick = function (event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        };
    }
});


document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append('username', document.getElementById('username').value);
    formData.append('password', document.getElementById('password').value);

    fetch('/login', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            window.location.href = '/home';
        } else {
            document.getElementById('login-error').innerText = data.message;
        }
    })
    .catch(error => console.error('Error:', error));
});

// Function to toggle the menu display
function toggleMenu() {
    const menuContainer = document.getElementById('menu-container');
    menuContainer.classList.toggle('show');
}

document.addEventListener('click', (event) => {
    console.log('Document clicked', event.target);
    const menuContainer = document.getElementById('menu-container');
    const menuIcon = document.querySelector('.menu-icon');
    if (
        menuContainer.classList.contains('show') &&
        !menuContainer.contains(event.target) &&
        !menuIcon.contains(event.target)
    ) {
        menuContainer.classList.remove('show');
    }
});

// Function to save changes in SYSTEMDETAILS table
function saveChanges() {
    const rows = document.querySelectorAll("#systemdetails-table tr[data-id]");
    const updatedData = [];

    rows.forEach(row => {
        const id = row.getAttribute("data-id");
        const hospitalName = row.cells[0].innerText.trim();
        const ward = row.cells[1].innerText.trim();
        const baudRate = row.cells[2].innerText.trim();
        const keepRecordDays = row.cells[3].innerText.trim();
        const centralServer = row.cells[4].innerText.trim();
        const maxRoom = row.cells[5].innerText.trim();
        const delay = row.cells[6].innerText.trim();
        const localIP = row.cells[7].innerText.trim();

        updatedData.push({
            id,
            hospital_name: hospitalName,
            ward,
            baudrate: baudRate,
            keep_record_days: keepRecordDays,
            centralserver: centralServer,
            maxroom: maxRoom,
            delay,
            localip: localIP
        });
    });

    fetch('/update_systemdetails', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ updatedData })
    })
    .then(response => {
        if (!response.ok) {
            // If the response is not OK (e.g., 403 Forbidden), throw an error
            return response.json().then(data => {
                throw new Error(data.error || "Failed to update system details.");
            });
        }
        return response.json();
    })
    .then(data => {
        alert("System details updated successfully!");
    })
    .catch(error => {
        // Display the error message returned by the server
        alert(error.message);
    });
}

// Function to save changes in BED_DETAILS table
function saveBedDetails() {
    const rows = document.querySelectorAll("#bed_details-table tr[data-id]");
    const updatedBedDetails = [];

    rows.forEach(row => {
        const bedID = row.getAttribute("data-id");
        const ipAddress = row.cells[2].innerText.trim();  // Adjusted index for IP Address
        const roomNo = row.cells[3].innerText.trim();      // Adjusted index for Room No
        const bedNo = row.cells[4].innerText.trim();       // Adjusted index for Bed No
        const bedType = row.querySelector("select").value; // Adjusted for the Bed Type dropdown

        updatedBedDetails.push({
            bed_id: bedID,
            ip_address: ipAddress,
            room_no: roomNo,
            bed_no: bedNo,
            bed_type: bedType
        });
    });

    fetch('/update_bed_details', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ updatedBedDetails })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.success ? "Bed details updated successfully!" : "Failed to update bed details.");
    })
    .catch(error => console.error("Error updating bed details:", error));
}



function addBed() {
    const bedID = document.getElementById("bedID").value;
    const ipAddress = document.getElementById("ipAddress").value;
    const roomNo = document.getElementById("roomNo").value;
    const bedNo = document.getElementById("bedNo").value;
    const bedType = document.getElementById("bedType").value;

    fetch('/add_bed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            bed_id: bedID,
            ip_address: ipAddress,
            room_no: roomNo,
            bed_no: bedNo,
            bed_type: bedType
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Bed added successfully!");
            closeAddBedForm();
            location.reload();
        } else {
            alert("Failed to add bed.");
        }
    })
    .catch(error => console.error("Error adding bed:", error));
}
function openAddBedForm(isEdit = false, bedID = null) {
    isEditing = isEdit;
    editingBedID = bedID;

    if (isEditing && bedID) {
        // Pre-fill form with bed details for editing
        const row = document.querySelector(`tr[data-id='${bedID}']`);
        document.getElementById("bedID").value = bedID;
        document.getElementById("ipAddress").value = row.cells[2].innerText.trim();
        document.getElementById("roomNo").value = row.cells[3].innerText.trim();
        document.getElementById("bedNo").value = row.cells[4].innerText.trim();
        document.getElementById("bedType").value = row.querySelector("select").value;
    } else {
        fetch('/next_bed_id')
            .then(response => response.json())
            .then(data => {
                document.getElementById("bedID").value = data.next_bed_id;
                document.getElementById("ipAddress").value = '';
                document.getElementById("roomNo").value = '';
                document.getElementById("bedNo").value = '';
                document.getElementById("bedType").value = 'bed';
            })
            .catch(error => console.error("Error fetching next BEDID:", error));
    }

    document.getElementById("addBedModal").style.display = "block";
}

function submitAddBed() {
    const bedID = document.getElementById("bedID").value;
    const ipAddress = document.getElementById("ipAddress").value;
    const roomNo = document.getElementById("roomNo").value;
    const bedNo = document.getElementById("bedNo").value;
    const bedType = document.getElementById("bedType").value;

    fetch('/add_bed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            bed_id: bedID,
            ip_address: ipAddress,
            room_no: roomNo,
            bed_no: bedNo,
            bed_type: bedType,
            is_editing: isEditing  // Pass edit flag
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(isEditing ? "Bed updated successfully!" : "Bed added successfully!");
            closeAddBedForm();
            location.reload();
        } else {
            alert(data.error || (isEditing ? "Failed to update bed." : "Failed to add bed."));
        }
    })
    .catch(error => console.error("Error adding/updating bed:", error));
}

function closeAddBedForm() {
    isEditing = false;
    editingBedID = null;
    document.getElementById("addBedModal").style.display = "none";
}

function editSelectedBed() {
    const selected = document.querySelectorAll(".bed-select-checkbox:checked");
    if (selected.length === 1) {
        const row = selected[0].closest("tr");
        const bedID = row.getAttribute("data-id");
        openAddBedForm(true, bedID);
    } else {
        alert("Select one bed to edit.");
    }
}
function deleteSelectedBeds() {
    const selectedBeds = [];
    document.querySelectorAll(".bed-select-checkbox:checked").forEach(checkbox => {
        const row = checkbox.closest("tr");
        selectedBeds.push(row.getAttribute("data-id"));
    });

    if (selectedBeds.length === 0) {
        alert("No beds selected for deletion.");
        return;
    }

    fetch('/delete_beds', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bed_ids: selectedBeds })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("Selected beds deleted successfully!");
            location.reload();
        } else {
            alert(data.error || "Failed to delete beds.");
        }
    })
    .catch(error => console.error("Error deleting beds:", error));
}


function searchLogs() {
    const ward = document.getElementById("ward").value;
    const callType = document.getElementById("callType").value;
    const fromDateTime = document.getElementById("fromDateTime").value;
    const toDateTime = document.getElementById("toDateTime").value;

    fetch(`/search_logs?ward=${ward}&callType=${callType}&fromDateTime=${fromDateTime}&toDateTime=${toDateTime}`)
        .then(response => response.json())
        .then(data => {
            const resultsBody = document.getElementById("resultsBody");
            resultsBody.innerHTML = "";

            data.forEach(record => {
                const row = `<tr>
                    <td>${record.ROOM_NO}</td>
                    <td>${record.BED_NO}</td>
                    <td>${record.WARD}</td>
                    <td>${record.STATUS}</td>
                    <td>${record.CALLTYPE}</td>
                    <td>${record.CALL_AT}</td>
                    <td>${record.SERVED_AT}</td>
                    <td>${record.TIME_TAKEN}</td>
                </tr>`;
                resultsBody.insertAdjacentHTML("beforeend", row);
            });
        })
        .catch(error => console.error("Error fetching logs:", error));
}

function downloadLogs() {
    const ward = document.getElementById("ward").value;
    const callType = document.getElementById("callType").value;
    const fromDateTime = document.getElementById("fromDateTime").value;
    const toDateTime = document.getElementById("toDateTime").value;

    // Pass filters as query parameters for Excel download
    window.location.href = `/download_excel?ward=${ward}&callType=${callType}&fromDateTime=${fromDateTime}&toDateTime=${toDateTime}`;
}

function handleLogout() {
    fetch('/logout', { method: 'GET' })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;  // Redirect to the index page on successful logout
            } else {
                console.error('Logout failed');
            }
        })
        .catch(error => console.error('Error:', error));
}

