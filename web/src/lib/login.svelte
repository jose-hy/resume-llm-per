<script lang="ts">
  import { invalidateAll } from "$app/navigation";
  import { post } from "../utils.js";
  import { formFunc } from "./loginForm.svelte.js";
  import * as v from "valibot";

  export const form = formFunc({
    email: v.pipe(v.string(), v.email("Invalid email")),
    password: v.pipe(
      v.string(),
      v.minLength(6, "Password must be at least 6 characters long")
    ),
  });

  let email = $state("");
  let password = $state("");

  const register = async () => {
    if (form.validate({ email, password })) {
      await post("/register", { username: email, password });
      invalidateAll();
    }
  };

  const login = async () => {
    post("/login", { username: email, password });
    invalidateAll();
  };
</script>

<div class="h-[100vh]">
  <form class="grid place-content-center bg-white">
    <label for="email">Email</label>
    <input
      class="[border:1px_solid_#DADADA] rounded-4px"
      bind:value={email}
      id="email"
    />
    <label for="password">Password</label>
    <p>{form.errors.email}</p>
    <input
      class="[border:1px_solid_#DADADA] rounded-4px"
      bind:value={password}
      id="password"
      type="password"
    />
    <p>{form.errors.password}</p>
    <button
      class="bg-black text-white rounded-4px px-12px py-4px w-full mx-auto"
      onclick={register}>Register</button
    >
    <button onclick={login}>Login</button>
  </form>
</div>
