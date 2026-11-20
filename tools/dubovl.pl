#!/usr/bin/env perl
# dubovl.pl - link Madlen files into static overlays under the Dubna monitor
# system (the dubna emulator, the system of monsys.9).
#
#     dubovl.pl [-v] [-p LIB.bin] OVL.bin 'scheme line'... -- file.asm... > listing
#     dubovl.pl [-v] -l LIB.bin file.asm... > listing
#
# The first form assembles the files and links them with *CALL OVERLAY into
# the overlay catalog of OVL.bin (unit 60), then prints the catalog. The
# scheme lines are those of *CALL OVERLAY: a line PARENT(A,B) puts the
# overlays A and B under PARENT, side by side (they load at the same
# address). Under /MONTRAN, the second resident (01000-01603, a library
# module), the root loads at 01604 as the compilers of monsys.9 do:
#     '/montran(fortran)' 'fortran(cbdpr,glink)'
# An overlay right under /MONTRAN needs a line of its own (its name alone
# if nothing is under it); a line naming an overlay of a lower level alone
# links it after its siblings instead of over them.
# -p: modules are also taken from the personal library LIB.bin (unit 66).
#
# The second form assembles the files into the personal library LIB.bin.
# The input of a job is limited to two drums (65536 words), so a link of
# many modules needs both.
#
# The .bin files are on *DISC:1/LOCAL: they must exist in the current
# directory and be large enough (zeros will do); a name is at most 6
# characters before .bin; *DISC and *FILE must be the first cards of the job.
# The job is left in dubovl.dub.
use utf8;
use feature 'unicode_strings';
use open ':encoding(UTF-8)';
use open ':std', ':encoding(UTF-8)';

$verbose = 0;
while (@ARGV) {
    if ($ARGV[0] eq '-v') { $verbose = 1; shift @ARGV; }
    elsif ($ARGV[0] eq '-p') { shift @ARGV; $perso = shift @ARGV; }
    elsif ($ARGV[0] eq '-l') { shift @ARGV; $tolib = shift @ARGV; }
    else { last; }
}
sub fname {
    my ($f) = @_;
    (my $n = $f) =~ s/\.bin$// or die "$f: not a .bin file\n";
    die "$f: no such file\n" unless -f $f;
    return $n;
}
if ($tolib) {
    die "Usage: dubovl.pl -l LIB.bin file.asm...\n" unless @ARGV;
    @files = @ARGV;
} else {
    die "Usage: dubovl.pl [-p LIB.bin] OVL.bin 'scheme'... -- file.asm...\n" if @ARGV < 3;
    $out = shift @ARGV;
    while (@ARGV && $ARGV[0] ne '--') { push @scheme, shift @ARGV; }
    shift @ARGV;
    @files = @ARGV;
    die "No Madlen files\n" unless @files;
}

$job = "dubovl.dub";
open(B, ">$job") || die "Cannot open $job for writing\n";
print B "*name dubovl\n*disc:1/local\n";
print B "*file:" . fname($tolib) . ",66,w\n" if $tolib;
print B "*file:" . fname($perso) . ",66\n" if $perso;
print B "*file:" . fname($out) . ",60,w\n" if $out;
print B "*perso:660000\n" if $perso;
print B "*no list\n" unless $verbose;
print B "*madlen\n";
for (@files) {
    open(F, $_) || die "Where did $_ go?\n";
    while (<F>) { print B unless /^\s*$/; }
    close(F);
}
if ($tolib) {
    print B "*to perso:660000\n*call plcatalog:660000\n";
} else {
    print B "*call overlay:600000\n";
    print B " $_\n" for @scheme;
    print B "*end record\n*call ocatalog:600000\n";
}
print B "*end file\n";
close(B);
exec("dubna", $job);
