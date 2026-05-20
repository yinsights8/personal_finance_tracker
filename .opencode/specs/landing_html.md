# Landing Page with Flip Card - Implementation Plan

---

## Overview

Create a single `landing.html` page with a **CSS flip card** containing:
- **Front**: Login form
- **Back**: Register form

The card flips on user interaction (click to switch between Login/Register).

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `templates/landing.html` | Create | Main landing page with flip card |
| `main.py` | Modify | Add `/` route redirecting to `/landing` |
| `plans/app-route-plan.md` | Modify | Update with landing page documentation |

---

## Landing Page Structure

```
┌─────────────────────────────────────────────────────┐
│                    Header                            │
│              (Logo / App Name)                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│           ┌─────────────────────┐                    │
│           │                     │                    │
│           │    FLIP CARD       │                    │
│           │                     │                    │
│           │  [Login Form]      │  ← Front          │
│           │                     │                    │
│           │  [Register Form]   │  ← Back (flipped)  │
│           │                     │                    │
│           └─────────────────────┘                    │
│                                                      │
│            "Don't have an account? Register"        │
│            "Already have an account? Login"         │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Flip Card Mechanics

### HTML Structure
```html
<div class="flip-card">
    <div class="flip-card-inner">
        <!-- Front (Login) -->
        <div class="flip-card-front">
            <form action="/auth/login" method="post">
                <!-- Login fields -->
            </form>
            <p class="toggle-link" onclick="flipCard()">Don't have an account? Register</p>
        </div>
        
        <!-- Back (Register) -->
        <div class="flip-card-back">
            <form action="/auth/register" method="post">
                <!-- Register fields -->
            </form>
            <p class="toggle-link" onclick="flipCard()">Already have an account? Login</p>
        </div>
    </div>
</div>
```

### CSS (flip animation)
```css
.flip-card {
    perspective: 1000px;
}
.flip-card-inner {
    transition: transform 0.6s;
    transform-style: preserve-3d;
}
.flip-card.flipped .flip-card-inner {
    transform: rotateY(180deg);
}
.flip-card-front, .flip-card-back {
    backface-visibility: hidden;
}
.flip-card-back {
    transform: rotateY(180deg);
}
```

### JavaScript
```javascript
function flipCard() {
    document.querySelector('.flip-card').classList.toggle('flipped');
}
```

---

## Login Form (Front of Card)

### Fields
| Field | Type | Name | Validation |
|-------|------|------|------------|
| Email | email | `email` | Required, valid email format |
| Password | password | `password` | Required |

### Buttons
- **Login** - Submit button
- **Toggle** - "Don't have an account? Register" (flips card)

### Error Handling (via URL param `?error=...`)
| Condition | Error Message |
|-----------|---------------|
| Email not found | "Email or password does not match" |
| Password incorrect | "Email or password does not match" |

### Form Action
```html
<form action="/auth/login" method="post">
```

---

## Register Form (Back of Card)

### Fields
| Field | Type | Name | Validation |
|-------|------|------|------------|
| Name | text | `name` | Required, 2-100 chars |
| Email | email | `email` | Required, valid email |
| Password | password | `password` | Required, min 8 chars |
| Confirm Password | password | `confirm_password` | Must match password |

### Buttons
- **Register** - Submit button
- **Toggle** - "Already have an account? Login" (flips card)

### Error Handling
| Condition | Error Message |
|-----------|---------------|
| Email already exists | "User already exists" |
| Password mismatch | "Passwords do not match" |
| Name too short | "Name must be 2-100 characters" |
| Password too short | "Password must be at least 8 characters" |

### Form Action
```html
<form action="/auth/register" method="post">
```

---

## Routes

### Route Changes

| Route | Change |
|-------|--------|
| `GET /` | Redirect to `/landing` |
| `GET /landing` | New: Render `landing.html` |
| `POST /auth/login` | On error, redirect to `/landing?error=...&card=login` |
| `POST /auth/register` | On error, redirect to `/landing?error=...&card=register` |

### Redirect Logic

```python
# Login error → go back to login side of card
RedirectResponse(url="/landing?error=Invalid+credentials&card=login", status_code=303)

# Register error → flip to register side and show error
RedirectResponse(url="/landing?error=User+already+exists&card=register", status_code=303)
```

---

## Error Display

### On Landing Page Load
```javascript
// Check URL params
const urlParams = new URLSearchParams(window.location.search);
const error = urlParams.get('error');
const card = urlParams.get('card');

// If error exists
if (error) {
    document.getElementById('error-message').textContent = error;
    document.getElementById('error-div').style.display = 'block';
}

// Flip card if needed
if (card === 'register') {
    document.querySelector('.flip-card').classList.add('flipped');
}
```

---

## Styling Requirements

Match existing `index.html` theme:
- Background: `rgb(21, 20, 20)`
- Text: `rgb(255, 255, 255)`
- Bootstrap 5 dark theme
- Card background: `rgb(40, 40, 40)`
- Submit buttons: Bootstrap secondary style
- Error text: Red (`#dc3545`)

### Card Dimensions
- Width: 400px (responsive)
- Height: Auto (based on content)
- Border-radius: 10px
- Padding: 2rem

---

## User Flow

### Login Flow
1. User visits `/` → Redirects to `/landing`
2. Login form visible (front of card)
3. User enters email/password
4. Clicks Login
5. Backend validates:
   - ✅ Email + Password correct → Redirect to `/`
   - ❌ Wrong credentials → Redirect to `/landing?error=Email+or+password+does+not+match&card=login`
6. Error displays on login form

### Register Flow
1. User visits `/` → Redirects to `/landing`
2. Clicks "Don't have an account? Register"
3. Card flips to show register form (back)
4. User enters name, email, password, confirm password
5. Clicks Register
6. Backend validates:
   - ❌ Email exists → Redirect to `/landing?error=User+already+exists&card=register`
   - ❌ Password mismatch → Redirect to `/landing?error=Passwords+do+not+match&card=register`
   - ✅ Success → Redirect to `/auth/login?success=Registration+successful`

---

## Implementation Order

1. Update `main.py` - Add `/` redirect and `/landing` route
2. Create `templates/landing.html` - HTML structure
3. Add CSS styles for flip card animation
4. Add JavaScript for card flipping and error handling
5. Test login flow
6. Test register flow
7. Update `plans/app-route-plan.md`

---

## Decisions (Final)

1. **Flip trigger**: Click on toggle text to flip card
2. **Success message**: Auto-login after successful registration
3. **Remember me**: Add "Remember me" checkbox with extended session (7 days)