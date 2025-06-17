<?php

namespace App\Http\Controllers\Admin;
use Illuminate\Support\Str;
use App\Models\Service;
use App\Models\User;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class ServiceController extends Controller
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

    public function store(Request $request)
    {
        $validated = $request->validate([            'name' => 'required|string|max:255',            'type' => 'required|string|max:100',            'description' => 'nullable|string',        ]);
        Service::create($validated);
        return redirect()->route('admin.services.index')->with('success', 'Service created.');
    }

    {
        //
    }

    /**
     * Store a newly created resource in storage.
     */

    /**
     * Display the specified resource.
     */
    public function show(string $id)

    public function update(Request $request, string $id)
    {
        $service = Service::findOrFail($id);
        $staffUsers = User::where('role', 'doctor')->orderBy('name')->get();
        $validated = $request->validate([            'name' => 'required|string|max:255',            'type' => 'required|string|max:100',            'description' => 'nullable|string',        ]);
        $service->update($validated);
        if($request->has('staff_ids')) { $service->staff()->sync($request->input('staff_ids', [])); } else { $service->staff()->detach(); }
        return redirect()->route('admin.services.index')->with('success', 'Service updated.');
    }

    {
        //
    }

    /**
     * Show the form for editing the specified resource.
     */
    public function edit(string $id)
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
