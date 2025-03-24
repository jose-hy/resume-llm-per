<script lang="ts">
  import { invalidateAll } from "$app/navigation";
  import { get, post } from "../utils.js";
  import { formFunc } from "./loginForm.svelte.js";
  import * as v from "valibot";
  import Spacer from "./spacer.svelte";

  export const form = formFunc({
    email: v.pipe(v.string(), v.email("Invalid email")),
    password: v.pipe(
      v.string(),
      v.minLength(6, "Password must be at least 6 characters long")
    ),
  });

  let email = $state("");
  let status = $state("sign in");
  let password = $state("");

  const register = async () => {
    if (form.validate({ email, password })) {
      await post("/register", { username: email, password });
      invalidateAll();
    }
  };

  const login = async () => {
    const res = await post("/login", { username: email, password });
    console.log(await res.text());
    invalidateAll();
  };

  const test = async () => {
    const res = await get("", {
      headers: {
        cookie:
          "accessCode=eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJnYXJldGhjbmdAZ21haWwuY29tIiwiaWF0IjoxNzQyNjQ3NDMxLCJleHAiOjE3NDI3MzM4MzF9.0k52UMiLCIcGrkBT1LI4m_6bwWrM8GhpkXNGosavQ10",
      },
    });
    console.log(await res.json());
  };
</script>

<div class="h-[100vh] grid place-content-center">
  <form
    class="bg-white px-20px py-24px rounded-[10px] [border:1px_solid_#DADADA] w-[90vw] max-w-[400px] flex flex-col items-center"
  >
    <!-- <button onclick={test}>test</button> -->
    <h1 class="text-center font-700 text-24px">Interview Moves</h1>
    <Spacer axis="y" size={24} />
    <div class="flex flex-col gap-4px w-full">
      <label class="font-600 text-15px" for="email">Email</label>
      <input
        class="[border:1px_solid_#DADADA] rounded-4px px-8px py-[6px]"
        bind:value={email}
        id="email"
      />
    </div>
    <p>{form.errors.email}</p>
    <Spacer axis="y" size={20} />
    <div class="flex flex-col gap-4px w-full">
      <label class="font-600 text-15px" for="password">Password</label>
      <input
        class="[border:1px_solid_#DADADA] rounded-4px px-8px py-[6px]"
        bind:value={password}
        id="password"
        type="password"
      />
    </div>
    <Spacer axis="y" size={24} />
    <p>{form.errors.password}</p>
    <button
      class="bg-black text-white rounded-8px px-12px py-8px w-full mx-auto"
      onclick={status === "sign in" ? login : register}
      >{status === "sign in" ? "Sign in" : "Register"}</button
    >
    <Spacer axis="y" size={24} />
    {#if status === "sign in"}
      <span class="">
        Need an account?
        <button class="font-600" onclick={() => (status = "sign up")}>
          Sign up</button
        >
      </span>
    {:else}
      <span>
        Have an account?
        <button class="font-600" onclick={() => (status = "sign in")}
          >Sign in</button
        >
      </span>
    {/if}
  </form>
</div>
