<script lang="ts">
	let last_name = $state('');	
	let first_name = $state('');
	let email = $state('');
	let pin = $state('');
	let password = $state('');
	let confirmPassword = $state('');
	let error = $state('');

	async function handleRegister() {
		error = '';
		if (!first_name || !last_name || !email || !pin || !password || !confirmPassword) {
			error = 'Please fill in all fields';
			return;
		}
		if (password !== confirmPassword) {
			error = 'Passwords do not match';
			return;
		}
		if (password.length < 8) {
			error = 'Password must be at least 8 characters';
			return;
		}
		console.log('Register with:', name, email);
	}
</script>

<main>
	<a href="/" class="back-btn" aria-label="Go back">
		<svg
			xmlns="http://www.w3.org/2000/svg"
			width="24"
			height="24"
			viewBox="0 0 24 24"
			fill="none"
			stroke="currentColor"
			stroke-width="2"
			stroke-linecap="round"
			stroke-linejoin="round"
		>
			<path d="M19 12H5" />
			<path d="M12 19L5 12L12 5" />
		</svg>
	</a>
	<div class="login-container">
		<h1>Create Account</h1>
		<form
			onsubmit={(e) => {
				e.preventDefault();
				handleRegister();
			}}
		>
			{#if error}
				<p class="error">{error}</p>
			{/if}
			<div class="field">
				<label for="flast_name">Last Name</label>
				<input type="text" id="last_name" bind:value={last_name} placeholder="Your last name" />
			</div>
			<div class="field">
				<label for="first_name">First Name</label>
				<input type="text" id="first_name" bind:value={first_name} placeholder="Your first name" />
			</div>
			<div class="field">
				<label for="email">Email</label>
				<input type="email" id="email" bind:value={email} placeholder="you@example.com" />
			</div>
			<div class="field">
				<label for="pin">Pin</label>
				<input type="password" id="pin" bind:value={pin} placeholder="Your Pin" />
			</div>
			<div class="field">
				<label for="password">Password</label>
				<input type="password" id="password" bind:value={password} placeholder="At least 8 characters" />
			</div>
			<div class="field">
				<label for="confirmPassword">Confirm Password</label>
				<input type="password" id="confirmPassword" bind:value={confirmPassword} placeholder="Repeat your password" />
			</div>
			<button type="submit" class="submit-btn">Create Account</button>
		</form>
			
		<div class="divider"></div>

		<p class="register-link">
			Already have an account? <a href="/login">Login</a>
		</p>
	</div>
</main>

<style>
	main {
		font-family: system-ui, sans-serif;
		min-height: 100vh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: #111;
		position: relative;
	}

	.back-btn {
		position: absolute;
		top: 1rem;
		left: 1rem;
		width: 48px;
		height: 48px;
		border-radius: 50%;
		background: white;
		color: #111;
		display: flex;
		align-items: center;
		justify-content: center;
		text-decoration: none;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
		transition:
			transform 0.2s ease,
			box-shadow 0.2s ease;
	}

	.back-btn:hover {
		transform: scale(1.1);
		box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
	}

	.login-container {
		background: white;
		padding: 2rem;
		border-radius: 10px;
		width: 100%;
		max-width: 400px;
	}

	h1 {
		text-align: center;
		margin-bottom: 1.5rem;
	}

	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.field {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	label {
		font-weight: 500;
	}

	input {
		padding: 0.75rem;
		border: 1px solid #ccc;
		border-radius: 6px;
		font-size: 1rem;
	}

	input:focus {
		outline: none;
		border-color: #111;
	}

	.error {
		color: #d32f2f;
		font-size: 0.875rem;
		text-align: center;
	}

	.register-link {
		text-align: center;
		margin-top: 1rem;
		font-size: 0.875rem;
	}

	.register-link a {
		color: #111;
		font-weight: 500;
	}

	.submit-btn {
		padding: 0.75rem 1.5rem;
		background: black;
		color: white;
		border: none;
		border-radius: 6px;
		cursor: pointer;
		font-size: 1rem;
	}

	.submit-btn:hover {
		opacity: 0.9;
	}

	.divider {
		display: flex;
		align-items: center;
		margin: 1.5rem 0;
		color: #666;
		font-size: 0.875rem;
	}

	.divider::before,
	.divider::after {
		content: '';
		flex: 1;
		height: 1px;
		background: #ddd;
	}
</style>
