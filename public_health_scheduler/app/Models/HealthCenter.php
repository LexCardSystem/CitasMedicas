<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use App\Models\Appointment;
use App\Models\User;
use Illuminate\Database\Eloquent\Model;

class HealthCenter extends Model
{
    use HasFactory;
    protected $casts = ['operating_hours' => 'array'];

    protected $fillable = [
        'name',
        'address',
        'contact_info',
    ];

    // Relationships can be defined here later (e.g., with Appointments, Staff)
}
