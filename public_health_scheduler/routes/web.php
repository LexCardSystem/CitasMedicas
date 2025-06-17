});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});
});

use App\Http\Controllers\Patient\AppointmentController;
});
});
});
});
});
});

// Patient specific routes (already within auth middleware group from manual setup)
Route::middleware(['auth'])->prefix('patient')->name('patient.')->group(function () {
    Route::get('appointments/create', [AppointmentController::class, 'create'])->name('appointments.create');
    Route::post('appointments', [AppointmentController::class, 'store'])->name('appointments.store');
    Route::get('appointments', [AppointmentController::class, 'index'])->name('appointments.index'); // To view their own appointments
});
