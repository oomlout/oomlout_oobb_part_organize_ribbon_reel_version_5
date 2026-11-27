$fn = 50;

difference() {
	union() {
		translate(v = [0, 0, 6.0]) {
			cylinder(h = 30, r = 7.5);
		}
		hull() {
			translate(v = [-15.0, 15.0, 0]) {
				cylinder(h = 6, r = 7);
			}
			translate(v = [15.0, 15.0, 0]) {
				cylinder(h = 6, r = 7);
			}
			translate(v = [-15.0, -15.0, 0]) {
				cylinder(h = 6, r = 7);
			}
			translate(v = [15.0, -15.0, 0]) {
				cylinder(h = 6, r = 7);
			}
		}
		translate(v = [-15, -15, 6.0]) {
			cylinder(h = 1.5, r = 2.75);
		}
		translate(v = [-15, -15, 7.5]) {
			cylinder(h = 1.5, r1 = 2.75, r2 = 1.25);
		}
		translate(v = [-15, 15, 6.0]) {
			cylinder(h = 1.5, r = 2.75);
		}
		translate(v = [-15, 15, 7.5]) {
			cylinder(h = 1.5, r1 = 2.75, r2 = 1.25);
		}
		translate(v = [15, -15, 6.0]) {
			cylinder(h = 1.5, r = 2.75);
		}
		translate(v = [15, -15, 7.5]) {
			cylinder(h = 1.5, r1 = 2.75, r2 = 1.25);
		}
		translate(v = [15, 15, 6.0]) {
			cylinder(h = 1.5, r = 2.75);
		}
		translate(v = [15, 15, 7.5]) {
			cylinder(h = 1.5, r1 = 2.75, r2 = 1.25);
		}
	}
	union() {
		translate(v = [-15, -7.5, 6]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [-7.5, -15, 6]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [-15, 7.5, 6]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [7.5, -15, 6]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [15, -7.5, 6]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [-7.5, 15, 6]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [15, 7.5, 6]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [7.5, 15, 6]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
						translate(v = [0, 0, -1.9]) {
							cylinder(h = 1.9, r1 = 1.8, r2 = 3.6);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.8);
						}
						translate(v = [0, 0, -6.0]) {
							cylinder(h = 6, r = 1.5);
						}
					}
					union();
				}
			}
		}
		translate(v = [0, 0, 36]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [-2.875, -5.0, -5.3]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, -5.6]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
						translate(v = [-2.875, -5.0, 0]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, 0.3]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
						translate(v = [0, 0, -5]) {
							linear_extrude(height = 5) {
								polygon(points = [[5.914249999999999, 0.0], [2.957125, 5.1218907443321156], [-2.9571249999999982, 5.1218907443321156], [-5.914249999999999, 7.242867331857232e-16], [-2.9571250000000022, -5.121890744332115], [2.9571249999999956, -5.121890744332118]]);
							}
						}
						translate(v = [-2.875, -5.0, -5.3]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, -5.6]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
						translate(v = [-2.875, -5.0, 0]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, 0.3]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
						translate(v = [-2.875, -5.0, -5.3]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, -5.6]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
						translate(v = [-2.875, -5.0, 0]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, 0.3]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
					}
					union();
				}
			}
		}
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						linear_extrude(height = 5.5) {
							polygon(points = [[5.914249999999999, 0.0], [2.957125, 5.1218907443321156], [-2.9571249999999982, 5.1218907443321156], [-5.914249999999999, 7.242867331857232e-16], [-2.9571250000000022, -5.121890744332115], [2.9571249999999956, -5.121890744332118]]);
						}
						translate(v = [-2.875, -5.0, -0.3]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, -0.6]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
						translate(v = [-2.875, -5.0, 5.5]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, 5.8]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
					}
					union();
				}
			}
		}
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [-2.875, -5.0, -0.3]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, -0.6]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
						translate(v = [-2.875, -5.0, 5]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, 5.3]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
					}
					union();
				}
			}
		}
		translate(v = [0, 0, 0]) {
			rotate(a = [0, 0, 0]) {
				difference() {
					union() {
						translate(v = [-2.875, -5.0, -0.3]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, -0.6]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
						translate(v = [-2.875, -5.0, 5]) {
							cube(size = [5.75, 10, 0.3]);
						}
						translate(v = [-2.875, -2.875, 5.3]) {
							cube(size = [5.75, 5.75, 0.3]);
						}
					}
					union();
				}
			}
		}
		translate(v = [15, 0, -0.1]) {
			cylinder(h = 6.2, r = 3.25);
		}
		translate(v = [-15, 0, -0.1]) {
			cylinder(h = 6.2, r = 3.25);
		}
		translate(v = [0, 15, -0.1]) {
			cylinder(h = 6.2, r = 3.25);
		}
		translate(v = [0, -15, -0.1]) {
			cylinder(h = 6.2, r = 3.25);
		}
		translate(v = [0, 0, -0.1]) {
			cylinder(h = 36.2, r = 3.25);
		}
	}
}
