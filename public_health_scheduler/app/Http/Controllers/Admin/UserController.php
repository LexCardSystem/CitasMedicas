<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rule;

class UserController extends Controller
    public function __construct()
    {
        $this->middleware(function ($request, $next) {
            if (!Auth::check() || Auth::user()->email !== '$ADMIN_EMAIL') {
                abort(403, 'Unauthorized action.');
            }
            return $next($request);
        });
    }
{
    /**
     * Display a listing of the resource.
     */
    public function index()
    {
        //
    }

    /**
     * Show the form for creating a new resource.
     */
    public function create()
    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */
    public function store(Request $request)
    {
        //
    }

    /**
     * Display the specified resource.
     */
    public function show(string $id)
    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(string $id)

    public function update(Request $request, string $id)
    {
        $user = User::findOrFail($id);
        $validated = $request->validate([            'name' => 'required|string|max:255',            'email' => ['required', 'string', 'email', 'max:255', Rule::unique('users')->ignore($user->id)],            'role' => 'required|string|in:patient,doctor,supervisor,admin',            'password' => 'nullable|string|min:8|confirmed',        ]);
        $user->name = $validated['name'];
        $user->email = $validated['email'];
        $user->role = $validated['role'];
        if (!empty($validated['password'])) {
            $user->password = Hash::make($validated['password']);
        }
        $user->save();
        return redirect()->route('admin.users.index')->with('success', 'User updated successfully.');
    }
    {
        //
    }

    /**
     * Update the specified resource in storage.
     */

    /**
     * Remove the specified resource from storage.
     */
    public function destroy(string $id)
    {
        //
    }
}
