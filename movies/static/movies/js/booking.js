/**
 * Cinema Ticket Booking & Review Portal
 * Interactive Seat Selection Matrix & Dynamic Price Calculation
 */

document.addEventListener("DOMContentLoaded", () => {
  initSeatBookingMatrix();
  initStarRatingWidget();
});

function initSeatBookingMatrix() {
  const seatGrid = document.getElementById("seatMatrixGrid");
  if (!seatGrid) return;

  const ticketPrice = parseFloat(seatGrid.dataset.ticketPrice || "0");
  const hiddenInput = document.getElementById("id_selected_seats");
  const seatCountDisplay = document.getElementById("selectedSeatCount");
  const seatListDisplay = document.getElementById("selectedSeatsList");
  const subtotalDisplay = document.getElementById("subtotalDisplay");
  const totalDisplay = document.getElementById("totalPriceDisplay");
  const submitBtn = document.getElementById("btnConfirmBooking");
  const emptyPlaceholder = document.getElementById("emptySeatsPlaceholder");

  let selectedSeats = new Set();

  // If there were previously submitted seats (e.g., after validation error)
  if (hiddenInput && hiddenInput.value.trim()) {
    const existing = hiddenInput.value.split(",").map(s => s.trim().toUpperCase()).filter(Boolean);
    existing.forEach(code => {
      const seatEl = seatGrid.querySelector(`[data-seat-code="${code}"]`);
      if (seatEl && !seatEl.classList.contains("seat-booked")) {
        selectedSeats.add(code);
        seatEl.classList.remove("seat-available");
        seatEl.classList.add("seat-selected");
      }
    });
    updateBookingSummary();
  }

  // Handle seat clicks using event delegation
  seatGrid.addEventListener("click", (e) => {
    const seatEl = e.target.closest(".seat-item");
    if (!seatEl) return;

    // Ignore already booked seats
    if (seatEl.classList.contains("seat-booked")) {
      seatEl.classList.add("shake-animation");
      setTimeout(() => seatEl.classList.remove("shake-animation"), 400);
      return;
    }

    const seatCode = seatEl.dataset.seatCode;
    if (!seatCode) return;

    if (selectedSeats.has(seatCode)) {
      // Deselect
      selectedSeats.delete(seatCode);
      seatEl.classList.remove("seat-selected");
      seatEl.classList.add("seat-available");
    } else {
      // Limit to e.g. 10 seats per booking
      if (selectedSeats.size >= 10) {
        alert("You can select a maximum of 10 seats per booking.");
        return;
      }
      // Select
      selectedSeats.add(seatCode);
      seatEl.classList.remove("seat-available");
      seatEl.classList.add("seat-selected");
    }

    updateBookingSummary();
  });

  // Function to remove a seat via chip in sidebar
  window.deselectSeat = function(code) {
    if (selectedSeats.has(code)) {
      selectedSeats.delete(code);
      const seatEl = seatGrid.querySelector(`[data-seat-code="${code}"]`);
      if (seatEl) {
        seatEl.classList.remove("seat-selected");
        seatEl.classList.add("seat-available");
      }
      updateBookingSummary();
    }
  };

  function updateBookingSummary() {
    const sortedSeats = Array.from(selectedSeats).sort();
    const count = sortedSeats.length;
    const total = (count * ticketPrice).toFixed(2);

    // Update hidden form field
    if (hiddenInput) {
      hiddenInput.value = sortedSeats.join(", ");
    }

    // Update seat count
    if (seatCountDisplay) {
      seatCountDisplay.textContent = count;
    }

    // Update prices
    if (subtotalDisplay) {
      subtotalDisplay.textContent = `$${total}`;
    }
    if (totalDisplay) {
      totalDisplay.textContent = `$${total}`;
    }

    // Update seats chip list
    if (seatListDisplay) {
      seatListDisplay.innerHTML = "";
      if (count === 0) {
        if (emptyPlaceholder) emptyPlaceholder.style.display = "block";
      } else {
        if (emptyPlaceholder) emptyPlaceholder.style.display = "none";
        sortedSeats.forEach(seat => {
          const chip = document.createElement("span");
          chip.className = "badge bg-warning text-dark p-2 me-1 mb-1 d-inline-flex align-items-center gap-1 shadow-sm";
          chip.innerHTML = `
            <strong>${seat}</strong>
            <button type="button" class="btn-close btn-close-dark ms-1" style="font-size: 0.6rem;" onclick="deselectSeat('${seat}')" aria-label="Remove"></button>
          `;
          seatListDisplay.appendChild(chip);
        });
      }
    }

    // Enable/disable submit button
    if (submitBtn) {
      submitBtn.disabled = count === 0;
      if (count === 0) {
        submitBtn.innerHTML = `Select Seats to Continue`;
      } else {
        submitBtn.innerHTML = `Book ${count} Seat${count > 1 ? 's' : ''} • $${total}`;
      }
    }
  }
}

/**
 * Interactive Star Rating Widget for Community Reviews
 */
function initStarRatingWidget() {
  const widget = document.getElementById("interactiveStarRating");
  if (!widget) return;

  const stars = widget.querySelectorAll(".star-btn");
  const ratingInput = document.getElementById("id_rating");
  const ratingText = document.getElementById("selectedRatingLabel");

  const ratingDescriptions = {
    1: "1 Star - Poor",
    2: "2 Stars - Below Average",
    3: "3 Stars - Average",
    4: "4 Stars - Very Good",
    5: "5 Stars - Masterpiece!"
  };

  let currentRating = ratingInput ? parseInt(ratingInput.value || "5") : 5;

  function highlightStars(rating) {
    stars.forEach(star => {
      const val = parseInt(star.dataset.value);
      if (val <= rating) {
        star.classList.remove("text-secondary");
        star.classList.add("text-warning");
        star.innerHTML = "★";
      } else {
        star.classList.remove("text-warning");
        star.classList.add("text-secondary");
        star.innerHTML = "☆";
      }
    });
    if (ratingText && ratingDescriptions[rating]) {
      ratingText.textContent = ratingDescriptions[rating];
    }
  }

  // Initialize
  highlightStars(currentRating);

  stars.forEach(star => {
    star.addEventListener("mouseenter", () => {
      const val = parseInt(star.dataset.value);
      highlightStars(val);
    });

    star.addEventListener("mouseleave", () => {
      highlightStars(currentRating);
    });

    star.addEventListener("click", () => {
      currentRating = parseInt(star.dataset.value);
      if (ratingInput) {
        ratingInput.value = currentRating;
      }
      highlightStars(currentRating);
    });
  });
}
