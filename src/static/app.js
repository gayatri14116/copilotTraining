document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Load activities when page loads
  loadActivities();
  loadActivityOptions();

  // Fetch and display activities
  async function loadActivities() {
    try {
      const response = await fetch("/activities", {
        cache: "no-cache"
      });
      const activities = await response.json();

      activitiesList.innerHTML = "";

      for (const [name, details] of Object.entries(activities)) {
        const card = createActivityCard(name, details);
        activitiesList.appendChild(card);
      }
    } catch (error) {
      console.error("Error loading activities:", error);
      activitiesList.innerHTML =
        '<p class="error">Failed to load activities. Please try again later.</p>';
    }
  }

  // Create an activity card with participants list
  function createActivityCard(name, details) {
    const card = document.createElement("div");
    card.className = "activity-card";

    const spotsLeft = details.max_participants - details.participants.length;

    // Build participants list HTML
    let participantsHTML = '<div class="participants"><h5>Participants:</h5>';
    if (details.participants.length > 0) {
      participantsHTML += "<ul>";
      details.participants.forEach((email) => {
        participantsHTML += `
          <li>
            ${email}
            <span class="delete-icon" data-activity="${name}" data-email="${email}" title="Unregister ${email}">✕</span>
          </li>`;
      });
      participantsHTML += "</ul>";
    } else {
      participantsHTML +=
        '<ul><li class="no-participants">No participants yet</li></ul>';
    }
    participantsHTML += "</div>";

    card.innerHTML = `
    <h4>${name}</h4>
    <p><strong>Description:</strong> ${details.description}</p>
    <p><strong>Schedule:</strong> ${details.schedule}</p>
    <p><strong>Spots available:</strong> ${spotsLeft} / ${details.max_participants}</p>
    ${participantsHTML}
  `;

    // Add event listeners for delete icons
    card.querySelectorAll('.delete-icon').forEach(icon => {
      icon.addEventListener('click', handleUnregister);
    });

    return card;
  }

  // Load activity options for the dropdown
  async function loadActivityOptions() {, {
        cache: "no-cache"
      }
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

   

  // Handle unregistering a participant
  async function handleUnregister(event) {
    const activityName = event.target.dataset.activity;
    const email = event.target.dataset.email;

    if (!confirm(`Are you sure you want to unregister ${email} from ${activityName}?`)) {
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activityName)}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Reload activities to show updated participants
        loadActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }   for (const name of Object.keys(activities)) {
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      }
    } catch (error) {
      console.error("Error loading activity options:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(
          email
        )}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Reload activities to show updated participants
        loadActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });
});
