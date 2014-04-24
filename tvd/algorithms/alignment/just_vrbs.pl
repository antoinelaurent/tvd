#!/usr/bin/perl

if(scalar(@ARGV) != 3){
	die "Usage : $0 fichierTxt(Node1-Node2#Speaker#text) fichierAudio name\n";
}

$txt = $ARGV[0];
$wav = $ARGV[1];
$name = $ARGV[2];

%map = ();
$map{"‘"}="'";
$map{"…"}="...";
$map{"–"}="-";
$map{"’"}="'";


open(OUT, ">/tmp/$name.txt");
open(TXT, $txt);
while($ligneC = <TXT>){
	chomp($ligneC);
	if($ligneC =~ /^[^#]+#[^#]+#(.*)/){
		$ligne = $1;
		print OUT nettoyerLigne($ligne)."\n";	
	}
}
close(TXT);
close(OUT);


$cmd = "cat /tmp/$name.txt | utf2iso 2> /tmp/$name.txt.iso.error 1> /dev/null";
system($cmd);

if(-s "/tmp/$name.txt.iso.error" > 0){
	die "Error during conversion ... see /tmp/$name.txt.iso.error"
}
unlink "/tmp/$name.txt.iso.error";

$cmd = "mkdir align";
system($cmd) if(!-d "align");

$cmd = "vrbs_align -l:eng -v -f $wav /tmp/$name.txt > /tmp/$name.xml";
system($cmd);


$cmd = "cat /tmp/$name.xml | xml2ctm";
system($cmd);
	
clean();

sub clean{
	unlink "/tmp/$name.txt";
	unlink "/tmp/$name.xml";
}


sub virerPonctuation{
	my $word = $_[0];
	$word =~ s/,//g;
    $word =~ s/\.//g;       
    $word =~ s/\?//g;       
    $word =~ s/\!//g;
	$word =~ s/\"//g;    
	$word =~ s/\://g;
	$word =~ s/\;//g;
	return trim($word);
}

sub trim{
        $chaine = $_[0];
        $chaine =~ s/^\s+//g;
        $chaine =~ s/\s+$//g;
        return $chaine;
}
sub nettoyerLigne{
        my $ligne=$_[0];
        foreach(keys %map){
                $ligne =~ s/$_/$map{$_}/g;
        }
        $ligne =~ s/\.\.\.([^\.])/\.\.\. $1/g;
        $ligne =~ s/ +/ /g;
        $ligne =~ s/\([^\)]+\)//g;
        $ligne =~ s/\[[^\]]+\]//g;
        return $ligne;
}
