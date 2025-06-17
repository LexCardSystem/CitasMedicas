<?php

namespace App\Http\Controllers\Admin;
use App\Models\HealthCenter;
use App\Models\User;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class HealthCenterController extends Controller
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
        $validated = $request->validate([            'name' => 'required|string|max:255',            'address' => 'required|string|max:255',            'contact_info' => 'nullable|string|max:255',        ]);
            'operating_hours_json' => 'nullable|json',
$data = $validated; unset($data['operating_hours_json']);        if (!empty($validated['operating_hours_json'])) { $data['operating_hours'] = json_decode($validated['operating_hours_json'], true); } else { $data['operating_hours'] = null; }        HealthCenter::create($data);
        return redirect()->route('admin.health-centers.index')->with('success', 'Health Center created.');
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
        $healthCenter = HealthCenter::findOrFail($id);
        $staffUsers = User::where('role', 'doctor')->orderBy('name')->get();
        $validated = $request->validate([            'name' => 'required|string|max:255',            'address' => 'required|string|max:255',            'contact_info' => 'nullable|string|max:255',        ]);
            'operating_hours_json' => 'nullable|json',
        $healthCenter->update($validated);
        if($request->has('staff_ids')) { $healthCenter->staff()->sync($request->input('staff_ids', [])); } else { $healthCenter->staff()->detach(); }
        return redirect()->route('admin.health-centers.index')->with('success', 'Health Center updated.');
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
